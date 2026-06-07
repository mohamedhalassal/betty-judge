import apiClient from "./client";
import type { Problem, ProblemCreate } from "@/lib/types";

export const problemsApi = {
  getAll: async (search?: string) => {
    const params = search ? { search } : {};
    const res = await apiClient.get<Problem[]>("/problems", { params });
    return res.data;
  },

  getById: async (id: number) => {
    const res = await apiClient.get<Problem>(`/problems/${id}`);
    return res.data;
  },

  create: async (data: ProblemCreate) => {
    const res = await apiClient.post<Problem>("/problems", data);
    return res.data;
  },

  update: async (id: number, data: ProblemCreate) => {
    const res = await apiClient.patch<Problem>(`/problems/${id}`, data);
    return res.data;
  },

  delete: async (id: number) => {
    const res = await apiClient.delete(`/problems/${id}`);
    return res.data;
  },
};
