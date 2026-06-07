import apiClient from "./client";
import type { SubmissionResponse, SubmissionCreate, SubmissionStatus } from "@/lib/types";

export const submissionsApi = {
  submit: async (data: SubmissionCreate) => {
    const res = await apiClient.post<SubmissionResponse>("/submit", data);
    return res.data;
  },

  getById: async (id: number) => {
    const res = await apiClient.get<SubmissionResponse>(`/my-submissions/${id}`);
    return res.data;
  },

  getAll: async (params?: {
    page?: number;
    size?: number;
    problem_id?: number;
    username?: string;
    verdict?: SubmissionStatus;
  }) => {
    const res = await apiClient.get<SubmissionResponse[]>("/submissions", { params });
    return res.data;
  },

  getMySubmissions: async (params?: {
    page?: number;
    size?: number;
    verdict?: SubmissionStatus;
  }) => {
    const res = await apiClient.get<SubmissionResponse[]>("/my-submissions", { params });
    return res.data;
  },
};
