"use client";
import { useState } from "react";
import { createContextEntry } from "../services/api";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

export default function ContextForm() {
  const [form, setForm] = useState({ content: "", source_type: "notes" });
  const router = useRouter();

  const handleChange = (e: any) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    await createContextEntry(form);
    toast.success("Context added!");
    router.push("/");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded shadow">
      <textarea
        name="content"
        placeholder="Context data..."
        value={form.content}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      />
      <select
        name="source_type"
        value={form.source_type}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      >
        <option value="notes">Notes</option>
        <option value="email">Email</option>
        <option value="whatsapp">WhatsApp</option>
      </select>
      <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
        Save Context
      </button>
    </form>
  );
}
