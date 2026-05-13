export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  problems_solved: number;
  total_submissions: number;
  acceptance_rate: number;
}
