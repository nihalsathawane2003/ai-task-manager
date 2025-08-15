"use client";
import { useEffect, useState } from "react";
import { getTasks } from "../services/api";
import TaskCard from "../components/TaskCard";
import Navbar from "../components/Navbar";

export default function Dashboard() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getTasks()
      .then((res) => {
        console.log("Tasks API Response:", res.data);

        // Handle both array and paginated formats
        if (Array.isArray(res.data)) {
          setTasks(res.data);
        } else if (Array.isArray(res.data.results)) {
          setTasks(res.data.results);
        } else {
          setError("Unexpected API response format");
          setTasks([]);
        }
      })
      .catch((err) => {
        console.error("Error fetching tasks:", err);
        setError("Failed to fetch tasks");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <>
      <Navbar />
      <div className="p-6 bg-gray-100 min-h-screen">
        <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

        {loading && <p>Loading tasks...</p>}
        {error && <p className="text-red-500">{error}</p>}

        {!loading && tasks.length === 0 && !error && (
          <p>No tasks found.</p>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tasks.map((task: any) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      </div>
    </>
  );
}
