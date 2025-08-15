import re
import math
import datetime as dt

URGENT_KEYWORDS = ["urgent", "asap", "today", "eod", "end of day", "important", "deadline", "overdue", "fix now"]
ESTIMATE_TABLE = {
    "bug": 2,
    "fix": 2,
    "email": 0.5,
    "report": 3,
    "meeting": 1,
    "deploy": 2,
    "feature": 5,
    "review": 1.5,
}

def naive_keywords(text):
    if not text:
        return []
    text = text.lower()
    tokens = re.findall(r"[a-z]{3,}", text)
    found = [t for t in tokens if t in ESTIMATE_TABLE or t in URGENT_KEYWORDS]
    # dedupe preserving order
    seen = set()
    out = []
    for w in found:
        if w not in seen:
            out.append(w); seen.add(w)
    return out

def sentiment_hint(text):
    if not text:
        return "neu"
    t = text.lower()
    if any(w in t for w in ["delay", "blocked", "issue", "angry", "complaint", "overdue", "fail"]):
        return "neg"
    if any(w in t for w in ["thanks", "thank you", "great", "appreciate", "good", "resolved"]):
        return "pos"
    return "neu"

def estimate_effort(title, description):
    text = f"{title or ''} {description or ''}".lower()
    hours = 0.5  # baseline half hour
    for k, h in ESTIMATE_TABLE.items():
        if k in text:
            hours += h
    # scale and clamp
    return min(max(0.5, hours), 40)

def priority_score(task, recent_context_list):
    # Baseline
    base = 30.0
    title = (task.get("title") or "").lower()
    desc = (task.get("description") or "").lower()
    combined = f"{title} {desc}"
    if any(k in combined for k in URGENT_KEYWORDS):
        base += 35
    if "bug" in combined or "prod" in combined or "production" in combined:
        base += 20
    # context urgency
    ctx_text = " ".join(recent_context_list).lower() if recent_context_list else ""
    if any(k in ctx_text for k in URGENT_KEYWORDS):
        base += 10
    # sentiment negative -> raise priority slightly
    if any(w in ctx_text for w in ["blocked", "overdue", "delay", "urgent"]):
        base += 8
    # penalty for long tasks (to make scheduling realistic)
    effort = estimate_effort(task.get("title", ""), task.get("description", ""))
    if effort > 8:
        base -= min(15, (effort - 8) * 1.5)
    # clamp
    return float(max(0.0, min(100.0, base)))

def suggest_deadline_iso(task, current_load_hours=0.0, recent_context_list=None):
    recent_context_list = recent_context_list or []
    effort = estimate_effort(task.get("title", ""), task.get("description", ""))
    urgent_bias = -1 if any(k in " ".join(recent_context_list).lower() for k in URGENT_KEYWORDS) else 0
    # estimate days needed relative to 6 productive hours/day
    days = math.ceil((effort + float(current_load_hours)) / 6.0) + urgent_bias
    days = max(0, days)  # allow 0 meaning today
    # If days==0 set to end of today (UTC)
    now = dt.datetime.utcnow()
    if days == 0:
        # set to end of day UTC ~ 23:59
        deadline = dt.datetime(now.year, now.month, now.day, 23, 59, 0)
    else:
        deadline = now + dt.timedelta(days=days)
    # return ISO with Z
    return deadline.replace(microsecond=0).isoformat() + "Z"
