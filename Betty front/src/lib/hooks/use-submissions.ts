import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { submissionsApi } from "@/lib/api/submissions";
import type { components } from "@/lib/types/api-schema";

type SubmissionCreate = components["schemas"]["SubmissionCreate"];

export function useSubmissions(params?: {
  page?: number;
  size?: number;
  problem_id?: number;
  username?: string;
  verdict?: components["schemas"]["SubmissionStatus"];
}) {
  return useQuery({
    queryKey: ["submissions", params],
    queryFn: () => submissionsApi.getAll(params),
    staleTime: 10 * 1000,
  });
}

export function useMySubmissions(params?: {
  page?: number;
  size?: number;
  verdict?: components["schemas"]["SubmissionStatus"];
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
      if (data && (data.verdict === "in_queue")) {
        return 2000;
      }
      return false;
    },
  });
}

export function useSubmitCode() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SubmissionCreate) => submissionsApi.submit(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["submissions"] });
    },
  });
}
