import apiClient from "./client";
import type { Submission, SubmissionListItem, SubmitCodePayload, PaginatedResponse } from "@/lib/types";

export const submissionsApi = {
  submit: async (data: SubmitCodePayload) => {
    const res = await apiClient.post<Submission>("/submissions", data);
    return res.data;
  },

  getById: async (id: number) => {
    const res = await apiClient.get<Submission>(`/submissions/${id}`);
    return res.data;
  },

  getAll: async (params?: {
    page?: number;
    limit?: number;
    problem_id?: number;
    user_id?: number;
    status?: string;
  }) => {
    const res = await apiClient.get<PaginatedResponse<SubmissionListItem>>("/submissions", {
      params,
    });
    return res.data;
  },

  getMySubmissions: async (params?: {
    page?: number;
    limit?: number;
    problem_id?: number;
  }) => {
    const res = await apiClient.get<PaginatedResponse<SubmissionListItem>>("/submissions/me", {
      params,
    });
    return res.data;
  },
};
