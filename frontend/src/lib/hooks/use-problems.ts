import { useQuery } from "@tanstack/react-query";
import { problemsApi } from "@/lib/api/problems";

export function useProblems(search?: string) {
  return useQuery({
    queryKey: ["problems", search],
    queryFn: () => problemsApi.getAll(search),
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
