export interface User {
  id: number;
  username: string;
  created_at: string;
}

export interface Problem {
  id: number;
  name: string;
  statement: string;
  created_at: string;
  created_by?: number;
  solution?: string | null;
  checker_code?: string | null;
  time_limit?: number;
  memory_limit?: number;
}

export interface ProblemCreate {
  name: string;
  statement: string;
  time_limit: number;
  memory_limit: number;
  solution?: string | null;
  checker_code?: string | null;
}

export type SubmissionStatus =
  | "in_queue"
  | "accepted"
  | "wrong_answer"
  | "time_limit_exceeded"
  | "runtime_error"
  | "compile_error"
  | "memory_limit_exceeded"
  | "idleness_limit_exceeded"
  | "failed";

export interface SubmissionCreate {
  problem_id: number;
  source_code: string;
}

export interface SubmissionResponse {
  id: number;
  user_id: number;
  source_code: string;
  problem_id: number;
  verdict: SubmissionStatus | null;
  execution_time: number | null;
  execution_memory: number | null;
  submitted_at: string;
}

export interface TestCaseCreate {
  input_data: string;
  expected_output: string;
  is_sample: boolean;
}

export interface TestCase {
  id: number;
  problem_id: number;
  input_data: string;
  expected_output: string;
  is_sample: boolean;
}

export interface ApiError {
  detail: string;
}
