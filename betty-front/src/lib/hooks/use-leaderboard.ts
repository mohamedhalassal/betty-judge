import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/lib/api/users";

export function useLeaderboard(params?: { page?: number; limit?: number }) {
  return useQuery({
    queryKey: ["leaderboard", params],
    queryFn: () => usersApi.getLeaderboard(params),
    staleTime: 30 * 1000,
  });
}
