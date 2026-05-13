export interface Submission {
  id: number;
  user_id: number;
  problem_id: number;
  source_code: string;
  submitted_at: string;
  execution_time: number | null;
  execution_memory: number | null;
  status: string | null;
  problem_name?: string;
  username?: string;
}

export interface SubmissionListItem {
  id: number;
  user_id: number;
  problem_id: number;
  problem_name: string;
  username: string;
  submitted_at: string;
  execution_time: number | null;
  execution_memory: number | null;
  status: string | null;
  language?: string;
}

export interface SubmitCodePayload {
  problem_id: number;
  source_code: string;
  language: string;
}

export type Verdict =
  | "Accepted"
  | "Wrong Answer"
  | "Time Limit Exceeded"
  | "Runtime Error"
  | "Compilation Error"
  | "Memory Limit Exceeded"
  | "Pending"
  | "Running";
