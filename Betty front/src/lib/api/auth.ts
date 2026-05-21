import apiClient from "./client";
import type { User } from "@/lib/types";

export const authApi = {
  login: async (token: string, username?: string) => {
    const url = username ? `/login?username=${encodeURIComponent(username)}` : "/login";
    const res = await apiClient.post<{ access_token: string; token_type: string }>(
      url,
      { token }
    );
    return res.data;
  },

  getMe: async (token?: string) => {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    const res = await apiClient.get<User>("/auth/me", config);
    return res.data;
  },

  logout: async () => {
    // The backend doesn't seem to have a logout endpoint, it relies on client dropping the token
    // So we just clear locally
    return { success: true };
  },
};
