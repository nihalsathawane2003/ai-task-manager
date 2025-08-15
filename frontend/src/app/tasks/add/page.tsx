"use client";
import Navbar from "../../../components/Navbar";
import TaskForm from "../../../components/TaskForm";

export default function AddTaskPage() {
  return (
    <>
      <Navbar />
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Add Task</h1>
        <TaskForm />
      </div>
    </>
  );
}
