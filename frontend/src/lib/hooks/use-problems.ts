import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { problemsApi } from "@/lib/api/problems";
import { useAuthStore } from "@/lib/store/auth-store";
import type { Problem, ProblemCreate } from "@/lib/types";

export function useProblems(params?: { search?: string; page?: number; size?: number }) {
  return useQuery({
    queryKey: ["problems", params],
    queryFn: () => problemsApi.getAll(params),
    staleTime: 30 * 1000,
  });
}

export function useProblem(id: number) {
  return useQuery({
    queryKey: ["problem", id],
    queryFn: () => problemsApi.getById(id),
    enabled: !!id,
    staleTime: 60 * 1000,
  });
}

export function useIsProblemOwner(problem?: Problem | null) {
  const userId = useAuthStore((s) => s.user?.id);
  return problem?.created_by != null && userId != null && problem.created_by === userId;
}

export function useCreateProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProblemCreate) => problemsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
    },
  });
}

export function useUpdateProblem(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProblemCreate) => problemsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
      queryClient.invalidateQueries({ queryKey: ["problem", id] });
    },
  });
}

export function useDeleteProblem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => problemsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
    },
  });
}
