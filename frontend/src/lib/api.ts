import axios, { type AxiosInstance } from "axios";

import { env } from "@/lib/env";
import { clearToken, getToken } from "@/lib/token";

/** Shared Axios instance pointed at the versioned API. */
export const api: AxiosInstance = axios.create({
  baseURL: `${env.apiBaseUrl}/v1`,
  headers: { "Content-Type": "application/json" },
});

// Attach the bearer token (if any) to every request.
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401, drop the (now invalid) token so the UI can redirect to login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      clearToken();
    }
    return Promise.reject(error);
  },
);
