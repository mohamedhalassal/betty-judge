export interface Problem {
  id: number;
  name: string;
  statement: string;
  created_at: string;
  created_by: number;
  solution: string | null;
  checker_code: string | null;
  test_cases?: TestCase[];
  tags?: string[];
}

export interface ProblemListItem {
  id: number;
  name: string;
  created_at: string;
  tags?: string[];
  difficulty?: string;
  acceptance_rate?: number;
  solved_by_user?: boolean;
}

export interface TestCase {
  id: number;
  problem_id: number;
  input_data: string;
  expected_output: string;
  is_sample: boolean;
}

export interface ProblemFilters {
  search?: string;
  difficulty?: string;
  tag?: string;
  status?: "all" | "solved" | "unsolved";
  page?: number;
  limit?: number;
}
