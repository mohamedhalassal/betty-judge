import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { submissionsApi } from "@/lib/api/submissions";
import type { SubmitCodePayload } from "@/lib/types";

export function useSubmissions(params?: {
  page?: number;
  limit?: number;
  problem_id?: number;
  user_id?: number;
  status?: string;
}) {
  return useQuery({
    queryKey: ["submissions", params],
    queryFn: () => submissionsApi.getAll(params),
    staleTime: 10 * 1000,
  });
}

export function useMySubmissions(params?: {
  page?: number;
  limit?: number;
  problem_id?: number;
}) {
  return useQuery({
    queryKey: ["submissions", "me", params],
    queryFn: () => submissionsApi.getMySubmissions(params),
    staleTime: 10 * 1000,
  });
}

export function useSubmission(id: number) {
  return useQuery({
    queryKey: ["submission", id],
    queryFn: () => submissionsApi.getById(id),
    enabled: !!id,
    staleTime: 5 * 1000,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data && (data.status === "Pending" || data.status === "Running")) {
        return 2000;
      }
      return false;
    },
  });
}

export function useSubmitCode() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SubmitCodePayload) => submissionsApi.submit(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["submissions"] });
    },
  });
}
