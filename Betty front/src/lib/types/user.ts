export interface User {
  id: number;
  google_id: string;
  username: string;
  created_at: string;
}

export interface UserProfile extends User {
  problems_solved: number;
  total_submissions: number;
  acceptance_rate: number;
  recent_submissions: SubmissionSummary[];
  solved_problems: ProblemSummary[];
}

export interface ProblemSummary {
  id: number;
  name: string;
}

export interface SubmissionSummary {
  id: number;
  problem_id: number;
  problem_name: string;
  status: string | null;
  submitted_at: string;
}
