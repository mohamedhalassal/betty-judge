"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/shared/page-header";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { TableSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { formatRelativeTime, formatExecutionTime } from "@/lib/utils";
import { useSubmissions } from "@/lib/hooks/use-submissions";
import type { SubmissionStatus } from "@/lib/types";

export default function SubmissionsPage() {
  const [statusFilter, setStatusFilter] = useState<SubmissionStatus | "all">("all");
  const [usernameFilter, setUsernameFilter] = useState("");
  const [problemIdFilter, setProblemIdFilter] = useState("");

  const filterParams = {
    verdict: statusFilter !== "all" ? statusFilter as SubmissionStatus : undefined,
    username: usernameFilter || undefined,
    problem_id: problemIdFilter ? parseInt(problemIdFilter, 10) : undefined,
  };

  const { data: submissions, isLoading, isError, refetch } = useSubmissions(filterParams);

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader
        title="All Submissions"
        description="View system-wide submissions"
      />

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col md:flex-row gap-4 mb-6"
      >
        <div className="flex flex-wrap gap-2">
          {["all", "accepted", "wrong_answer", "time_limit_exceeded", "in_queue"].map((s) => (
            <Button
              key={s}
              size="sm"
              variant={statusFilter === s ? "default" : "secondary"}
              onClick={() => setStatusFilter(s as SubmissionStatus | "all")}
              className="text-xs capitalize"
            >
              {s.replace(/_/g, " ")}
            </Button>
          ))}
        </div>
        <div className="flex flex-1 gap-4">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-muted" />
            <Input
              placeholder="Username..."
              value={usernameFilter}
              onChange={(e) => setUsernameFilter(e.target.value)}
              className="pl-9 h-9"
            />
          </div>
          <div className="relative w-32">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-muted" />
            <Input
              placeholder="Problem ID"
              type="number"
              value={problemIdFilter}
              onChange={(e) => setProblemIdFilter(e.target.value)}
              className="pl-9 h-9"
            />
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-border bg-card overflow-hidden"
      >
        <div className="grid grid-cols-[1fr_120px_80px_100px] gap-4 px-6 py-3 text-xs font-medium text-foreground-subtle uppercase tracking-wider border-b border-border bg-card-elevated">
          <div>Problem</div>
          <div className="text-center">Verdict</div>
          <div className="text-center hidden sm:block">Time</div>
          <div className="text-right">When</div>
        </div>

        {isLoading ? (
          <div className="p-4"><TableSkeleton columns={4} rows={5} /></div>
        ) : isError ? (
          <ErrorState title="Failed to load submissions" onRetry={() => refetch()} />
        ) : !submissions || submissions.length === 0 ? (
          <EmptyState
            title="No submissions"
            description="No submissions match your filters."
          />
        ) : (
          (Array.isArray(submissions) ? submissions : []).map((submission, index) => (
            <motion.div
              key={submission.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.03 }}
            >
              <Link
                href={`/submissions/${submission.id}`}
                className="grid grid-cols-[1fr_120px_80px_100px] gap-4 px-6 py-4 items-center hover:bg-card-hover border-b border-border/50 transition-colors group"
              >
                <div>
                  <span className="text-sm font-medium group-hover:text-primary transition-colors">
                    Problem #{submission.problem_id}
                  </span>
                </div>
                <div className="flex justify-center">
                  <VerdictBadge status={submission.verdict || "in_queue"} />
                </div>
                <div className="text-center text-sm text-foreground-muted hidden sm:block">
                  {formatExecutionTime(submission.execution_time)}
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
