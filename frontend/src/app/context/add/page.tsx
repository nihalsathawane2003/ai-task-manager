"use client";
import Navbar from "../../../components/Navbar";
import ContextForm from "../../../components/ContextForm";

export default function AddContextPage() {
  return (
    <>
      <Navbar />
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Add Context</h1>
        <ContextForm />
      </div>
    </>
  );
}
