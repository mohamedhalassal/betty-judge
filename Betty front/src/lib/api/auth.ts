import apiClient from "./client";
import type { User } from "@/lib/types";

export const authApi = {
  getGoogleLoginUrl: () =>
    `${apiClient.defaults.baseURL}/auth/google/login`,

  handleCallback: async (code: string) => {
    const res = await apiClient.post<{ access_token: string; user: User }>(
      "/auth/google/callback",
      { code }
    );
    return res.data;
  },

  getMe: async () => {
    const res = await apiClient.get<User>("/auth/me");
    return res.data;
  },

  logout: async () => {
    const res = await apiClient.post("/auth/logout");
    return res.data;
  },
};
