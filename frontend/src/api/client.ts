import axios from "axios";
import { ElNotification } from "element-plus";

const client = axios.create({
  baseURL: "/api/v1",
  timeout: 120000,
  withCredentials: true,
});

let _rateLimitTimer: ReturnType<typeof setTimeout> | null = null;

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail || "";

    if (status === 429) {
      if (!_rateLimitTimer) {
        ElNotification({
          title: "Rate Limited",
          message: "Too many requests. Please wait a moment before retrying.",
          type: "warning",
          duration: 5000,
        });
        _rateLimitTimer = setTimeout(() => {
          _rateLimitTimer = null;
        }, 5000);
      }
      return Promise.reject(error);
    }

    const message = detail || error.message || "Network error";
    console.error("[API Error]", message);
    return Promise.reject(error);
  }
);

export default client;
