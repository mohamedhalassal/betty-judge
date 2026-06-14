"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/shared/page-header";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { TableSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { formatRelativeTime, formatExecutionTime, formatMemory } from "@/lib/utils";
import { useSubmissions } from "@/lib/hooks/use-submissions";
import type { SubmissionStatus } from "@/lib/types";

const ALL_VERDICTS: { value: SubmissionStatus | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "accepted", label: "AC" },
  { value: "wrong_answer", label: "WA" },
  { value: "time_limit_exceeded", label: "TLE" },
  { value: "runtime_error", label: "RTE" },
  { value: "compile_error", label: "CE" },
  { value: "memory_limit_exceeded", label: "MLE" },
  { value: "idleness_limit_exceeded", label: "ILE" },
  { value: "failed", label: "FAIL" },
  { value: "in_queue", label: "Q" },
];

const PAGE_SIZE = 20;

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export default function SubmissionsPage() {
  const [statusFilter, setStatusFilter] = useState<SubmissionStatus | "all">("all");
  const [usernameInput, setUsernameInput] = useState("");
  const [problemIdInput, setProblemIdInput] = useState("");
  const [page, setPage] = useState(1);

  const debouncedUsername = useDebounce(usernameInput, 300);
  const debouncedProblemId = useDebounce(problemIdInput, 300);

  const filterParams = {
    verdict: statusFilter !== "all" ? (statusFilter as SubmissionStatus) : undefined,
    username: debouncedUsername || undefined,
    problem_id: debouncedProblemId ? parseInt(debouncedProblemId, 10) : undefined,
    page,
    size: PAGE_SIZE,
  };

  const { data: submissions, isLoading, isError, refetch } = useSubmissions(filterParams);

  const handlePrev = useCallback(() => setPage((p) => Math.max(1, p - 1)), []);
  const handleNext = useCallback(() => setPage((p) => p + 1), []);

  const hasMore = Array.isArray(submissions) && submissions.length === PAGE_SIZE;

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
        className="space-y-4 mb-6"
      >
        <div className="flex flex-wrap gap-1.5">
          {ALL_VERDICTS.map((v) => (
            <Button
              key={v.value}
              size="sm"
              variant={statusFilter === v.value ? "default" : "secondary"}
              onClick={() => { setStatusFilter(v.value); setPage(1); }}
              className="text-[11px] px-2.5 h-7"
            >
              {v.label}
            </Button>
          ))}
        </div>
        <div className="flex gap-4">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-muted" />
            <Input
              placeholder="Username..."
              value={usernameInput}
              onChange={(e) => { setUsernameInput(e.target.value); setPage(1); }}
              className="pl-9 h-9"
            />
          </div>
          <div className="relative w-32">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-muted" />
            <Input
              placeholder="Problem ID"
              type="number"
              value={problemIdInput}
              onChange={(e) => setProblemIdInput(e.target.value)}
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
        <div className="grid grid-cols-[1fr_120px_80px_80px_100px] gap-4 px-6 py-3 text-xs font-medium text-foreground-subtle uppercase tracking-wider border-b border-border bg-card-elevated">
          <div>Problem</div>
          <div className="text-center">Verdict</div>
          <div className="text-center hidden sm:block">Time</div>
          <div className="text-center hidden sm:block">Memory</div>
          <div className="text-right">When</div>
        </div>

        {isLoading ? (
          <div className="p-4"><TableSkeleton columns={5} rows={5} /></div>
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
                className="grid grid-cols-[1fr_120px_80px_80px_100px] gap-4 px-6 py-4 items-center hover:bg-card-hover border-b border-border/50 transition-colors group"
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

      <div className="flex items-center justify-center gap-4 mt-6">
        <Button
          size="sm"
          variant="outline"
          onClick={handlePrev}
          disabled={page <= 1}
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </Button>
        <span className="text-sm text-foreground-muted">Page {page}</span>
        <Button
          size="sm"
          variant="outline"
          onClick={handleNext}
          disabled={!hasMore}
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
