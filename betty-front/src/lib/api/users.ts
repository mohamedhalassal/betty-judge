import apiClient from "./client";
import type { UserProfile, PaginatedResponse, LeaderboardEntry } from "@/lib/types";

export const usersApi = {
  getProfile: async (username: string) => {
    const res = await apiClient.get<UserProfile>(`/users/${username}`);
    return res.data;
  },

  getLeaderboard: async (params?: { page?: number; limit?: number }) => {
    const res = await apiClient.get<PaginatedResponse<LeaderboardEntry>>("/users/leaderboard", {
      params,
    });
    return res.data;
  },
};
