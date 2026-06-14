import apiClient from "./client";
import type { SubmissionResponse, SubmissionCreate, SubmissionStatus } from "@/lib/types";

const TS_TO_BACKEND: Record<string, string> = {
  in_queue: "in queue",
  accepted: "accepted",
  wrong_answer: "wrong answer",
  time_limit_exceeded: "time limit exceeded",
  runtime_error: "runtime error",
  compile_error: "compile error",
  memory_limit_exceeded: "memory limit exceeded",
  idleness_limit_exceeded: "idleness limit exceeded",
  failed: "failed",
};

const BACKEND_TO_TS: Record<string, SubmissionStatus> = {};
for (const [ts, bk] of Object.entries(TS_TO_BACKEND)) {
  BACKEND_TO_TS[bk] = ts as SubmissionStatus;
}

function toBackendParams(params?: Record<string, unknown>): Record<string, unknown> | undefined {
  if (!params) return undefined;
  const mapped: Record<string, unknown> = {};
  for (const [key, val] of Object.entries(params)) {
    if (val === undefined) continue;
    mapped[key] = key === "verdict" && typeof val === "string" ? (TS_TO_BACKEND[val] ?? val) : val;
  }
  return mapped;
}

function normalizeSubmission(s: SubmissionResponse): SubmissionResponse {
  const v = s.verdict;
  if (v && BACKEND_TO_TS[v]) {
    return { ...s, verdict: BACKEND_TO_TS[v] };
  }
  return s;
}

function normalizeSubmissions(data: SubmissionResponse | SubmissionResponse[]): SubmissionResponse | SubmissionResponse[] {
  if (Array.isArray(data)) return data.map(normalizeSubmission);
  return normalizeSubmission(data);
}

export const submissionsApi = {
  submit: async (data: SubmissionCreate) => {
    const res = await apiClient.post<SubmissionResponse>("/submit", data);
    return normalizeSubmission(res.data);
  },

  getById: async (id: number) => {
    const res = await apiClient.get<SubmissionResponse>(`/my-submissions/${id}`);
    return normalizeSubmission(res.data);
  },

  getAll: async (params?: {
    page?: number;
    size?: number;
    problem_id?: number;
    username?: string;
    verdict?: SubmissionStatus;
  }) => {
    const res = await apiClient.get<SubmissionResponse[]>("/submissions", { params: toBackendParams(params as Record<string, unknown>) });
    return normalizeSubmissions(res.data) as SubmissionResponse[];
  },

  getMySubmissions: async (params?: {
    page?: number;
    size?: number;
    verdict?: SubmissionStatus;
  }) => {
    const res = await apiClient.get<SubmissionResponse[]>("/my-submissions", { params: toBackendParams(params as Record<string, unknown>) });
    return normalizeSubmissions(res.data) as SubmissionResponse[];
  },
};
