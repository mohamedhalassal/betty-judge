import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { testCasesApi } from "@/lib/api/test-cases";
import type { TestCaseCreate } from "@/lib/types";

export function useTestCases(problemId: number) {
  return useQuery({
    queryKey: ["test-cases", problemId],
    queryFn: () => testCasesApi.getByProblem(problemId),
    enabled: !!problemId,
  });
}

export function useCreateTestCase(problemId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TestCaseCreate) => testCasesApi.create(problemId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["test-cases", problemId] });
    },
  });
}

export function useUpdateTestCase(problemId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TestCaseCreate }) =>
      testCasesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["test-cases", problemId] });
    },
  });
}

export function useDeleteTestCase(problemId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => testCasesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["test-cases", problemId] });
    },
  });
}
