import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/lib/api/auth";

export function useProfile(username: string) {
  return useQuery({
    queryKey: ["users", username],
    queryFn: authApi.getMe,
    enabled: false,
    staleTime: 5 * 60 * 1000,
  });
}
