export default function TaskCard({ task }: { task: any }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow hover:shadow-lg transition">
      <h2 className="text-lg font-bold">{task.title}</h2>
      <p className="text-gray-600">{task.description}</p>
      <div className="flex justify-between mt-2">
        <span className="text-sm text-blue-500">{task.category}</span>
        <span
          className={`text-sm font-bold ${
            task.priority_score > 7 ? "text-red-500" : "text-green-500"
          }`}
        >
          Priority: {task.priority_score}
        </span>
      </div>
    </div>
  );
}
