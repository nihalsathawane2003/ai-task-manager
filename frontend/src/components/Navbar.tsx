"use client";
import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-blue-600 text-white p-4 flex justify-between">
      <h1 className="text-xl font-bold">Smart Todo</h1>
      <div className="space-x-4">
        <Link href="/">Dashboard</Link>
        <Link href="/tasks/add">Add Task</Link>
        <Link href="/context/add">Add Context</Link>
      </div>
    </nav>
  );
}
