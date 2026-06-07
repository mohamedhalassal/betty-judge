import { useQuery } from "@tanstack/react-query";

export function useLeaderboard() {
  return useQuery({
    queryKey: ["leaderboard"],
    queryFn: async () => ({ items: [] }),
    enabled: false,
    staleTime: 30 * 1000,
  });
}
