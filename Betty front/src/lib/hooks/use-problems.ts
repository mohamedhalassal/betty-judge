import { useQuery } from "@tanstack/react-query";
import { problemsApi } from "@/lib/api/problems";
import type { ProblemFilters } from "@/lib/types";

export function useProblems(filters?: ProblemFilters) {
  return useQuery({
    queryKey: ["problems", filters],
    queryFn: () => problemsApi.getAll(filters),
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
