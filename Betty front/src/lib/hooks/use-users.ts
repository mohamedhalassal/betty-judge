import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/lib/api/users";

export function useProfile(username: string) {
  return useQuery({
    queryKey: ["users", username],
    queryFn: () => usersApi.getProfile(username),
    enabled: !!username,
    staleTime: 5 * 60 * 1000,
  });
}

export function useLeaderboard(params?: { page?: number; limit?: number }) {
  return useQuery({
    queryKey: ["leaderboard", params],
    queryFn: () => usersApi.getLeaderboard(params),
    staleTime: 5 * 60 * 1000,
  });
}
