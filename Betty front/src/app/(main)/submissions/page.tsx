"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search, Filter } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/shared/page-header";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { formatRelativeTime, formatExecutionTime, formatMemory } from "@/lib/utils";

// Mock data
const mockSubmissions = [
  { id: 1, problem_id: 1, problem_name: "Two Sum", username: "user1", status: "Accepted", language: "C++", execution_time: 42, execution_memory: 8400, submitted_at: "2026-05-12T10:30:00Z" },
  { id: 2, problem_id: 2, problem_name: "Add Two Numbers", username: "user1", status: "Wrong Answer", language: "Python", execution_time: 156, execution_memory: 12800, submitted_at: "2026-05-12T10:25:00Z" },
  { id: 3, problem_id: 3, problem_name: "Longest Substring", username: "user1", status: "Time Limit Exceeded", language: "Java", execution_time: 2000, execution_memory: 65536, submitted_at: "2026-05-12T09:45:00Z" },
  { id: 4, problem_id: 1, problem_name: "Two Sum", username: "user1", status: "Compilation Error", language: "C++", execution_time: null, execution_memory: null, submitted_at: "2026-05-12T09:30:00Z" },
  { id: 5, problem_id: 4, problem_name: "Median of Two Sorted Arrays", username: "user1", status: "Runtime Error", language: "C++", execution_time: 15, execution_memory: 5600, submitted_at: "2026-05-11T22:15:00Z" },
  { id: 6, problem_id: 7, problem_name: "Container With Most Water", username: "user1", status: "Accepted", language: "Python", execution_time: 89, execution_memory: 15200, submitted_at: "2026-05-11T20:30:00Z" },
  { id: 7, problem_id: 9, problem_name: "Valid Parentheses", username: "user1", status: "Accepted", language: "C++", execution_time: 3, execution_memory: 3200, submitted_at: "2026-05-11T18:00:00Z" },
  { id: 8, problem_id: 5, problem_name: "Longest Palindromic Substring", username: "user1", status: "Memory Limit Exceeded", language: "Java", execution_time: 1200, execution_memory: 262144, submitted_at: "2026-05-10T14:20:00Z" },
];

export default function SubmissionsPage() {
  const [statusFilter, setStatusFilter] = useState("all");

  const filtered = mockSubmissions.filter((s) => {
    if (statusFilter === "all") return true;
    return s.status === statusFilter;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader
        title="My Submissions"
        description="View your submission history and results"
      />

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-wrap gap-2 mb-6"
      >
        {["all", "Accepted", "Wrong Answer", "Time Limit Exceeded", "Runtime Error", "Compilation Error"].map((s) => (
          <Button
            key={s}
            size="sm"
            variant={statusFilter === s ? "default" : "secondary"}
            onClick={() => setStatusFilter(s)}
            className="text-xs"
          >
            {s === "all" ? "All" : s}
          </Button>
        ))}
      </motion.div>

      {/* Submissions Table */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-border bg-card overflow-hidden"
      >
        {/* Header */}
        <div className="grid grid-cols-[1fr_120px_80px_80px_100px] gap-4 px-6 py-3 text-xs font-medium text-foreground-subtle uppercase tracking-wider border-b border-border bg-card-elevated">
          <div>Problem</div>
          <div className="text-center">Verdict</div>
          <div className="text-center hidden sm:block">Time</div>
          <div className="text-center hidden sm:block">Memory</div>
          <div className="text-right">When</div>
        </div>

        {filtered.length === 0 ? (
          <EmptyState
            title="No submissions"
            description="Start solving problems to see your submissions here."
          />
        ) : (
          filtered.map((submission, index) => (
            <motion.div
              key={submission.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.03 }}
            >
              <Link
                href={`/submissions/${submission.id}`}
                className="grid grid-cols-[1fr_120px_80px_80px_100px] gap-4 px-6 py-4 items-center hover:bg-card-hover border-b border-border/50 transition-colors group"
              >
                <div>
                  <span className="text-sm font-medium group-hover:text-primary transition-colors">
                    {submission.problem_name}
                  </span>
                  <div className="text-xs text-foreground-subtle mt-0.5">
                    {submission.language}
                  </div>
                </div>
                <div className="flex justify-center">
                  <VerdictBadge status={submission.status} />
                </div>
                <div className="text-center text-sm text-foreground-muted hidden sm:block">
                  {formatExecutionTime(submission.execution_time)}
                </div>
                <div className="text-center text-sm text-foreground-muted hidden sm:block">
                  {formatMemory(submission.execution_memory)}
                </div>
                <div className="text-right text-xs text-foreground-subtle">
                  {formatRelativeTime(submission.submitted_at)}
                </div>
              </Link>
            </motion.div>
          ))
        )}
      </motion.div>
    </div>
  );
}
