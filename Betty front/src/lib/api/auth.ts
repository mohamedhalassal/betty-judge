import apiClient from "./client";
import type { User } from "@/lib/types";

export const authApi = {
  login: async (token: string) => {
    const res = await apiClient.post<{ access_token: string; token_type: string }>(
      "/login",
      { token }
    );
    return res.data;
  },

  getMe: async () => {
    const res = await apiClient.get<User>("/me");
    return res.data;
  },

  updateUsername: async (username: string) => {
    const res = await apiClient.patch<User>("/me/username", { username });
    return res.data;
  },

  logout: async () => {
    return { success: true };
  },
};
