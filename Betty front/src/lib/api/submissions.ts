import apiClient from "./client";
import type { components } from "@/lib/types/api-schema";

type SubmissionResponse = components["schemas"]["SubmissionResponse"];
type SubmissionCreate = components["schemas"]["SubmissionCreate"];

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
    verdict?: components["schemas"]["SubmissionStatus"];
  }) => {
    const res = await apiClient.get<SubmissionResponse[]>("/submissions", {
      params,
    });
    return res.data;
  },

  getMySubmissions: async (params?: {
    page?: number;
    size?: number;
    verdict?: components["schemas"]["SubmissionStatus"];
  }) => {
    const res = await apiClient.get<SubmissionResponse[]>("/my-submissions", {
      params,
    });
    return res.data;
  },
};

