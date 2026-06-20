import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/store/auth-store";
import { toast } from "sonner";

export function useProfile() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const token = useAuthStore((s) => s.token);

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: authApi.getMe,
    enabled: isAuthenticated && !!token,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useUpdateUsername() {
  const queryClient = useQueryClient();
  const setUser = useAuthStore((s) => s.setUser);

  return useMutation({
    mutationFn: (username: string) => authApi.updateUsername(username),
    onSuccess: (user) => {
      setUser(user);
      queryClient.setQueryData(["auth", "me"], user);
      toast.success("Username updated successfully");
    },
    onError: (error: unknown) => {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to update username";
      toast.error(message);
    },
  });
}
