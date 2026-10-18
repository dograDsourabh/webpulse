import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? "http://localhost:8000" : "");

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 90000,
});

export async function createAudit(url) {
  if (!API_BASE_URL) {
    throw new Error(
      "The WebPulse analysis service is not configured for this deployment.",
    );
  }

  const response = await api.post("/api/audit", {
    url,
  });

  return response.data;
}
