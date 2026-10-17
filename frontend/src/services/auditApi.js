import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 90000,
});

export async function createAudit(url) {
  const response = await api.post("/api/audit", {
    url,
  });

  return response.data;
}