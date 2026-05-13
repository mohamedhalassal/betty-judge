import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/lib/api/users";

export function useUserProfile(username: string) {
  return useQuery({
    queryKey: ["user", username],
    queryFn: () => usersApi.getProfile(username),
    enabled: !!username,
    staleTime: 60 * 1000,
  });
}
