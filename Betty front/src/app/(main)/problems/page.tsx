"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search, CheckCircle2, Circle, Filter } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/shared/page-header";
import { TableSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { EmptyState } from "@/components/shared/empty-state";
import { useProblems } from "@/lib/hooks/use-problems";
import { cn } from "@/lib/utils";
import type { ProblemFilters } from "@/lib/types";

// Mock data for demo (will be replaced with API data)
const mockProblems = [
  { id: 1, name: "Two Sum", difficulty: "Easy", acceptance_rate: 78.5, solved_by_user: true, tags: ["Array", "Hash Table"] },
  { id: 2, name: "Add Two Numbers", difficulty: "Medium", acceptance_rate: 42.3, solved_by_user: false, tags: ["Linked List", "Math"] },
  { id: 3, name: "Longest Substring Without Repeating Characters", difficulty: "Medium", acceptance_rate: 35.1, solved_by_user: true, tags: ["String", "Sliding Window"] },
  { id: 4, name: "Median of Two Sorted Arrays", difficulty: "Hard", acceptance_rate: 22.8, solved_by_user: false, tags: ["Array", "Binary Search"] },
  { id: 5, name: "Longest Palindromic Substring", difficulty: "Medium", acceptance_rate: 33.7, solved_by_user: false, tags: ["String", "DP"] },
  { id: 6, name: "Regular Expression Matching", difficulty: "Hard", acceptance_rate: 18.2, solved_by_user: false, tags: ["String", "DP"] },
  { id: 7, name: "Container With Most Water", difficulty: "Medium", acceptance_rate: 55.4, solved_by_user: true, tags: ["Array", "Two Pointers"] },
  { id: 8, name: "3Sum", difficulty: "Medium", acceptance_rate: 32.6, solved_by_user: false, tags: ["Array", "Sorting"] },
  { id: 9, name: "Valid Parentheses", difficulty: "Easy", acceptance_rate: 81.2, solved_by_user: true, tags: ["Stack", "String"] },
  { id: 10, name: "Merge Two Sorted Lists", difficulty: "Easy", acceptance_rate: 72.9, solved_by_user: true, tags: ["Linked List", "Recursion"] },
  { id: 11, name: "Maximum Subarray", difficulty: "Medium", acceptance_rate: 50.1, solved_by_user: false, tags: ["Array", "DP"] },
  { id: 12, name: "Binary Tree Inorder Traversal", difficulty: "Easy", acceptance_rate: 74.6, solved_by_user: true, tags: ["Tree", "DFS"] },
];

const difficultyColor: Record<string, string> = {
  Easy: "text-success",
  Medium: "text-warning",
  Hard: "text-destructive",
};

export default function ProblemsPage() {
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  // Will use API data when backend is connected
  // const { data, isLoading, isError, refetch } = useProblems(filters);

  const filtered = mockProblems.filter((p) => {
    if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
    if (difficulty !== "all" && p.difficulty !== difficulty) return false;
    if (statusFilter === "solved" && !p.solved_by_user) return false;
    if (statusFilter === "unsolved" && p.solved_by_user) return false;
    return true;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader
        title="Problems"
        description="Practice algorithmic challenges and sharpen your skills"
      />

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-3 mb-6"
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-subtle" />
          <Input
            placeholder="Search problems..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2">
          {["all", "Easy", "Medium", "Hard"].map((d) => (
            <Button
              key={d}
              size="sm"
              variant={difficulty === d ? "default" : "secondary"}
              onClick={() => setDifficulty(d)}
              className="capitalize"
            >
              {d === "all" ? "All" : d}
            </Button>
          ))}
        </div>
        <div className="flex gap-2">
          {["all", "solved", "unsolved"].map((s) => (
            <Button
              key={s}
              size="sm"
              variant={statusFilter === s ? "default" : "secondary"}
              onClick={() => setStatusFilter(s)}
              className="capitalize"
            >
              {s}
            </Button>
          ))}
        </div>
      </motion.div>

      {/* Problems Table */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-border bg-card overflow-hidden"
      >
        {/* Table Header */}
        <div className="grid grid-cols-[48px_1fr_100px_120px_48px] sm:grid-cols-[48px_1fr_100px_120px_120px] gap-4 px-4 sm:px-6 py-3 text-xs font-medium text-foreground-subtle uppercase tracking-wider border-b border-border bg-card-elevated">
          <div className="text-center">#</div>
          <div>Title</div>
          <div className="text-center">Difficulty</div>
          <div className="text-center hidden sm:block">Acceptance</div>
          <div className="text-center">Status</div>
        </div>

        {/* Table Body */}
        {filtered.length === 0 ? (
          <EmptyState
            title="No problems found"
            description="Try adjusting your filters or search query."
          />
        ) : (
          filtered.map((problem, index) => (
            <motion.div
              key={problem.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.02 }}
            >
              <Link
                href={`/problems/${problem.id}`}
                className="grid grid-cols-[48px_1fr_100px_120px_48px] sm:grid-cols-[48px_1fr_100px_120px_120px] gap-4 px-4 sm:px-6 py-4 items-center hover:bg-card-hover border-b border-border/50 transition-colors duration-150 group"
              >
                <div className="text-center text-sm text-foreground-muted">
                  {problem.id}
                </div>
                <div>
                  <span className="text-sm font-medium group-hover:text-primary transition-colors">
                    {problem.name}
                  </span>
                  <div className="flex gap-1.5 mt-1">
                    {problem.tags?.slice(0, 2).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-[10px] px-1.5 py-0">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="text-center">
                  <span className={cn("text-sm font-medium", difficultyColor[problem.difficulty || ""])}>
                    {problem.difficulty}
                  </span>
                </div>
                <div className="text-center text-sm text-foreground-muted hidden sm:block">
                  {problem.acceptance_rate?.toFixed(1)}%
                </div>
                <div className="flex justify-center">
                  {problem.solved_by_user ? (
                    <CheckCircle2 className="h-5 w-5 text-success" />
                  ) : (
                    <Circle className="h-5 w-5 text-foreground-subtle/30" />
                  )}
                </div>
              </Link>
            </motion.div>
          ))
        )}
      </motion.div>
    </div>
  );
}
