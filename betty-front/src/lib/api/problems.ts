import apiClient from "./client";
import type { Problem, ProblemListItem, ProblemFilters, PaginatedResponse } from "@/lib/types";

export const problemsApi = {
  getAll: async (filters?: ProblemFilters) => {
    const res = await apiClient.get<PaginatedResponse<ProblemListItem>>("/problems", {
      params: filters,
    });
    return res.data;
  },

  getById: async (id: number) => {
    const res = await apiClient.get<Problem>(`/problems/${id}`);
    return res.data;
  },

  create: async (data: Partial<Problem>) => {
    const res = await apiClient.post<Problem>("/problems", data);
    return res.data;
  },

  update: async (id: number, data: Partial<Problem>) => {
    const res = await apiClient.put<Problem>(`/problems/${id}`, data);
    return res.data;
  },

  delete: async (id: number) => {
    const res = await apiClient.delete(`/problems/${id}`);
    return res.data;
  },
};
