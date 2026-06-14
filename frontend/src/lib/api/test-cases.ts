import apiClient from "./client";
import type { TestCase, TestCaseCreate } from "@/lib/types";

export const testCasesApi = {
  getAll: async () => {
    const res = await apiClient.get<TestCase[]>("/test_cases");
    return res.data;
  },

  getByProblem: async (problemId: number) => {
    const res = await apiClient.get<TestCase[]>(`/test_cases/problem/${problemId}`);
    return res.data;
  },

  getById: async (id: number) => {
    const res = await apiClient.get<TestCase>(`/test_cases/${id}`);
    return res.data;
  },

  create: async (problemId: number, data: TestCaseCreate) => {
    const res = await apiClient.post<TestCase>(`/test_cases/problem/${problemId}`, data);
    return res.data;
  },

  update: async (id: number, data: TestCaseCreate) => {
    const res = await apiClient.patch<TestCase>(`/test_cases/${id}`, data);
    return res.data;
  },

  delete: async (id: number) => {
    const res = await apiClient.delete(`/test_cases/${id}`);
    return res.data;
  },
};
