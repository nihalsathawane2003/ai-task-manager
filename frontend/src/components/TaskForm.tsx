"use client";

import { useState } from "react";
import { createTask, getAISuggestions } from "../services/api";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

export default function TaskForm() {
  const categories = [
    { id: 1, name: "Meetings" },
    { id: 2, name: "Writing" },
    { id: 3, name: "Urgent" },
    { id: 4, name: "Bugs" },
    { id: 5, name: "General" },
  ];

  const [form, setForm] = useState({
    title: "",
    description: "",
    category: "", // numeric ID as string
    deadline: "",
    priority_score: "",
    tags: "",
    sentiment: "",
    explanation: "",
  });

  const [loadingAI, setLoadingAI] = useState(false);
  const router = useRouter();

  const handleChange = (e: any) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const formatDateForBackend = (dateStr: string) => {
    if (!dateStr) return dateStr;
    if (/^\d{4}-\d{2}-\d{2}/.test(dateStr)) return dateStr;
    if (dateStr.includes("-")) {
      const [day, month, year] = dateStr.split("-");
      return `${year}-${month}-${day}`;
    }
    if (dateStr.includes("/")) {
      const [day, month, year] = dateStr.split("/");
      return `${year}-${month}-${day}`;
    }
    return dateStr;
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();

    const payload: any = {
      title: form.title,
      description: form.description,
      category: Number(form.category) || null,
      deadline: formatDateForBackend(form.deadline),
      priority_score: form.priority_score,
    };

    if (form.tags.trim()) payload.tags = form.tags;
    if (form.sentiment.trim()) payload.sentiment = form.sentiment;
    if (form.explanation.trim()) payload.explanation = form.explanation;

    try {
      await createTask(payload);
      toast.success("Task created!");
      router.push("/");
    } catch (error: any) {
      console.error("Task creation failed:", error.response?.data || error.message);
      toast.error("Task creation failed. Check console for details.");
    }
  };

  const handleAISuggestions = async () => {
    setLoadingAI(true);
    try {
      const payload = { title: form.title, description: form.description };
      const res = await getAISuggestions(payload);

      const formattedDeadline = formatDateForBackend(res.data.deadline?.slice(0, 10));

      // Safely handle AI category suggestion
      const aiCategoryName = Array.isArray(res.data.category_suggestions)
        ? res.data.category_suggestions[0]
        : undefined;

      const matchedCategory =
        typeof aiCategoryName === "string"
          ? categories.find(c => c.name.toLowerCase() === aiCategoryName.toLowerCase())
          : undefined;

      setForm(prev => ({
        ...prev,
        title: res.data.title || prev.title,
        description: res.data.enhanced_description || prev.description,
        category: matchedCategory?.id.toString() || prev.category,
        deadline: formattedDeadline || prev.deadline,
        priority_score: res.data.priority_score?.toString() || prev.priority_score,
        tags: res.data.tags?.join(", ") || prev.tags,
        sentiment: res.data.sentiment || prev.sentiment,
        explanation: res.data.explanation || prev.explanation,
      }));

      toast.success("AI suggestions applied!");
    } catch (err) {
      console.error("AI Suggest error:", err);
      toast.error("AI suggestion failed");
    } finally {
      setLoadingAI(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded shadow">
      <input
        name="title"
        placeholder="Title"
        value={form.title}
        onChange={handleChange}
        className="w-full p-2 border rounded"
        required
      />
      <textarea
        name="description"
        placeholder="Description"
        value={form.description}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      />
      <select
        name="category"
        value={form.category}
        onChange={handleChange}
        className="w-full p-2 border rounded"
        required
      >
        <option value="">Select Category</option>
        {categories.map(c => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
      <input
        type="text"
        name="deadline"
        placeholder="YYYY-MM-DD"
        value={form.deadline}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        name="priority_score"
        placeholder="Priority Score"
        value={form.priority_score}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        name="tags"
        placeholder="Tags (comma separated)"
        value={form.tags}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        name="sentiment"
        placeholder="Sentiment"
        value={form.sentiment}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        name="explanation"
        placeholder="Explanation"
        value={form.explanation}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      />
      <div className="flex space-x-2">
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Save Task
        </button>
        <button
          type="button"
          onClick={handleAISuggestions}
          className="bg-green-500 text-white px-4 py-2 rounded"
          disabled={loadingAI}
        >
          {loadingAI ? "Loading..." : "AI Suggest"}
        </button>
      </div>
    </form>
  );
}
