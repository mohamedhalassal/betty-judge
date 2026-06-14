import apiClient from "./client";
import type { TestCase, TestCaseCreate } from "@/lib/types";

export const testCasesApi = {
  getByProblem: async (problemId: number) => {
    const res = await apiClient.get<TestCase[]>(`/test_cases/problem/${problemId}`);
    return res.data;
  },

  create: async (problemId: number, data: TestCaseCreate) => {
    const res = await apiClient.post<TestCase>(`/test_cases/problem/${problemId}`, data);
    return res.data;
  },

  delete: async (id: number) => {
    await apiClient.delete(`/test_cases/${id}`);
  },
};
