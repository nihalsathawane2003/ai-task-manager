import os
import json
import requests
from .heuristics import naive_keywords, sentiment_hint, priority_score, suggest_deadline_iso
from todos.models import Category

# Config
USE_LM_STUDIO = os.getenv("USE_LM_STUDIO", "false").lower() in ("1", "true")
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() in ("1", "true")

LM_URL = os.getenv("LM_URL", "http://localhost:1234/v1/chat/completions")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

SYSTEM_PROMPT = (
    "You are an assistant that improves task descriptions, suggests realistic deadlines, "
    "priority (0-100), and categories/tags based on the user's recent context (messages/emails/notes). "
    "Return ONLY valid JSON when asked in JSON format."
)

def call_llm(messages):
    # Gemini
    if USE_GEMINI and GOOGLE_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        full_prompt = "\n".join([m["content"] for m in messages])
        response = model.generate_content(full_prompt)
        return response.text.strip()

    # LM Studio
    if USE_LM_STUDIO:
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": os.getenv("LM_MODEL", "local-model"),
            "messages": messages,
            "temperature": float(os.getenv("LM_TEMPERATURE", "0.2")),
            "max_tokens": int(os.getenv("LM_MAX_TOKENS", "512"))
        }
        resp = requests.post(LM_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0 and "message" in data["choices"][0]:
            return data["choices"][0]["message"]["content"]
        if "result" in data:
            return data["result"]
        return json.dumps(data)

    # OpenAI
    if OPENAI_API_KEY:
        import openai
        openai.api_key = OPENAI_API_KEY
        completion = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "512"))
        )
        return completion.choices[0].message.content

    return ""

def parse_llm_json(text):
    import json, re
    if not text:
        return {}
    try:
        return json.loads(text)
    except:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except:
                pass
    return {}

def get_category_id(category_name: str):
    try:
        cat = Category.objects.get(name=category_name)
        return cat.id
    except Category.DoesNotExist:
        return None

def suggest_for_task(payload: dict):
    task = payload.get("task", {}) or {}
    context_window = payload.get("context_window", []) or []
    preferences = payload.get("preferences", {}) or {}
    current_load = float(payload.get("current_load_hours", 0.0))

    # Heuristic baseline
    base_priority = priority_score(task, context_window)
    base_deadline = suggest_deadline_iso(task, current_load, context_window)
    tags = list(dict.fromkeys(
        naive_keywords(task.get("description", "") or "") +
        naive_keywords(" ".join(context_window))
    ))

    # Heuristic category guess
    category_guess_name = "Urgent" if base_priority >= 70 else (
        "Bugs" if "bug" in (task.get("title", "").lower() + task.get("description", "").lower())
        else "General"
    )
    category_id = get_category_id(category_guess_name)

    enhanced = task.get("description") or (task.get("title") or "")
    sentiment = sentiment_hint(" ".join(context_window))

    result = {
        "priority_score": float(base_priority),
        "deadline": base_deadline,
        "category_suggestions": [category_id] if category_id else [],
        "tags": tags[:6],
        "enhanced_description": enhanced,
        "sentiment": sentiment,
        "explanation": "heuristic"
    }

    # LLM refinement
    if USE_GEMINI or USE_LM_STUDIO or OPENAI_API_KEY:
        user_prompt = (
            f"Task Title: {task.get('title','')}\n"
            f"Task Description: {task.get('description','')}\n"
            f"Current load hours: {current_load}\n"
            f"Preferences: {preferences}\n"
            f"Recent context (last {len(context_window)}):\n" +
            "\n".join(context_window) + "\n\n"
            "Return a JSON with keys: priority_score (0-100 numeric), deadline (ISO8601), "
            "category_suggestions (list of category names), tags (list), enhanced_description (string). "
            "Keep deadlines realistic relative to current load and context. Only return JSON."
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        try:
            llm_text = call_llm(messages)
            parsed = parse_llm_json(llm_text)

            # Map category names to IDs
            if "category_suggestions" in parsed:
                category_ids = []
                for cat_name in parsed["category_suggestions"]:
                    cid = get_category_id(cat_name)
                    if cid:
                        category_ids.append(cid)
                parsed["category_suggestions"] = category_ids

            for k in ["priority_score", "deadline", "category_suggestions", "tags", "enhanced_description"]:
                if k in parsed and parsed[k]:
                    result[k] = parsed[k]
            result["explanation"] = "llm_refined"
        except Exception:
            pass

    # Ensure numeric priority_score
    try:
        result["priority_score"] = float(result.get("priority_score", 0.0))
    except:
        result["priority_score"] = base_priority

    return result
