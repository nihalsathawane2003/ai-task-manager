import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000/api", // Change to your backend URL
});

// TASKS
export const getTasks = () => API.get("/tasks/");
export const createTask = (data: any) => API.post("/tasks/", data);

// CONTEXT
export const getContextEntries = () => API.get("/context/");
export const createContextEntry = (data: any) => API.post("/context/", data);

export const getCategories = () => API.get("/categories/");
export const createCategory = (data: any) => API.post("/categories/", data);
// AI SUGGESTIONS
export const getAISuggestions = (taskData: any) =>
  API.post("/ai/suggest/", taskData);
