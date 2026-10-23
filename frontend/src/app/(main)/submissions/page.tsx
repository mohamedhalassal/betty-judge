"use client";

import { useState, useCallback, useEffect, useMemo, useRef, useSyncExternalStore } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { useQueries, useQuery } from "@tanstack/react-query";
import { Search, ChevronLeft, ChevronRight, X, User as UserIcon, BookOpen } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/shared/page-header";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { TableSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { cn, formatRelativeTime, formatDateTime, formatExecutionTime, formatMemory } from "@/lib/utils";
import { useSubmissions } from "@/lib/hooks/use-submissions";
import { problemsApi } from "@/lib/api/problems";
import { useAuthStore } from "@/lib/store/auth-store";
import type { Problem, SubmissionStatus } from "@/lib/types";

const ALL_VERDICTS: { value: SubmissionStatus | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "accepted", label: "Accepted" },
  { value: "wrong_answer", label: "Wrong Answer" },
  { value: "time_limit_exceeded", label: "Time Limit" },
  { value: "runtime_error", label: "Runtime Error" },
  { value: "compile_error", label: "Compile Error" },
  { value: "memory_limit_exceeded", label: "Memory Limit" },
  { value: "idleness_limit_exceeded", label: "Idleness Limit" },
  { value: "failed", label: "Failed" },
  { value: "in_queue", label: "In Queue" },
];

const PAGE_SIZE = 20;

const noopSubscribe = () => () => {};

const ROW_GRID =
  "grid grid-cols-[1fr_110px_90px] sm:grid-cols-[64px_1fr_160px_130px_80px_90px_110px] gap-4 items-center";

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

function ProblemPicker({
  selected,
  onSelect,
  canSearch,
}: {
  canSearch: boolean;
  selected: { id: number; name?: string } | null;
  onSelect: (problem: { id: number; name?: string } | null) => void;
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const debouncedQuery = useDebounce(query.trim(), 250);

  const idQuery = /^#?\d+$/.test(debouncedQuery) ? parseInt(debouncedQuery.replace("#", ""), 10) : null;
  const searchParams = { search: debouncedQuery || undefined, size: 8 };
  // /problems requires auth and a 401 redirects to /login, so only search when logged in
  const { data: results, isFetching } = useQuery({
    queryKey: ["problems", searchParams],
    queryFn: () => problemsApi.getAll(searchParams),
    enabled: canSearch && open && idQuery === null,
    staleTime: 30 * 1000,
  });

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const pick = (problem: { id: number; name?: string }) => {
    onSelect(problem);
    setQuery("");
    setOpen(false);
  };

  if (selected) {
    return (
      <div className="flex h-9 items-center gap-2 rounded-lg border border-primary/40 bg-primary/10 px-3 text-sm min-w-0">
        <BookOpen className="h-4 w-4 shrink-0 text-primary" />
        <span className="truncate">
          <span className="text-foreground-muted">#{selected.id}</span> {selected.name ?? ""}
        </span>
        <button
          type="button"
          onClick={() => onSelect(null)}
          className="ml-auto shrink-0 rounded p-0.5 text-foreground-muted hover:text-foreground hover:bg-card"
          aria-label="Clear problem filter"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-muted" />
      <Input
        placeholder="Search problem by name or #id..."
        value={query}
        onFocus={() => setOpen(true)}
        onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
        onKeyDown={(e) => {
          if (e.key === "Escape") setOpen(false);
          if (e.key === "Enter") {
            e.preventDefault();
            if (idQuery !== null) pick({ id: idQuery });
            else if (results && results.length > 0) pick(results[0]);
          }
        }}
        className="pl-9 h-9"
      />
      {open && (
        <div className="absolute z-20 mt-1 w-full overflow-hidden rounded-lg border border-border bg-card shadow-lg">
          {idQuery !== null ? (
            <button
              type="button"
              onClick={() => pick({ id: idQuery })}
              className="block w-full px-3 py-2 text-left text-sm hover:bg-card-hover"
            >
              Filter by problem <span className="font-medium">#{idQuery}</span>
            </button>
          ) : !canSearch ? (
            <div className="px-3 py-2 text-sm text-foreground-muted">Log in to search by name, or type a problem #id</div>
          ) : isFetching && !results ? (
            <div className="px-3 py-2 text-sm text-foreground-muted">Searching...</div>
          ) : !results || results.length === 0 ? (
            <div className="px-3 py-2 text-sm text-foreground-muted">No problems found</div>
          ) : (
            results.map((p: Problem) => (
              <button
                key={p.id}
                type="button"
                onClick={() => pick(p)}
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-card-hover"
              >
                <span className="w-10 shrink-0 text-xs text-foreground-subtle">#{p.id}</span>
                <span className="truncate">{p.name}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default function SubmissionsPage() {
  const currentUser = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  // false during SSR, true on the client — avoids hydration mismatch with persisted auth
  const mounted = useSyncExternalStore(noopSubscribe, () => true, () => false);

  const [statusFilter, setStatusFilter] = useState<SubmissionStatus | "all">("all");
  const [usernameInput, setUsernameInput] = useState("");
  const [username, setUsername] = useState("");
  const [problem, setProblem] = useState<{ id: number; name?: string } | null>(null);
  const [page, setPage] = useState(1);

  const filterParams = {
    verdict: statusFilter !== "all" ? statusFilter : undefined,
    username: username || undefined,
    problem_id: problem?.id,
    page,
    size: PAGE_SIZE,
  };

  const { data, isLoading, isError, isFetching, refetch } = useSubmissions(filterParams);
  const submissions = useMemo(() => (Array.isArray(data) ? data : []), [data]);

  const problemIds = useMemo(
    () => Array.from(new Set(submissions.map((s) => s.problem_id))),
    [submissions],
  );
  const problemQueries = useQueries({
    queries: problemIds.map((id) => ({
      queryKey: ["problem", id],
      queryFn: () => problemsApi.getById(id),
      staleTime: 60 * 1000,
      retry: false,
      enabled: mounted && isAuthenticated,
    })),
  });
  const problemNames = useMemo(() => {
    const map = new Map<number, string>();
    problemQueries.forEach((q, i) => {
      if (q.data?.name) map.set(problemIds[i], q.data.name);
    });
    return map;
  }, [problemQueries, problemIds]);

  const applyUsername = (value: string) => {
    setUsername(value.trim().toLowerCase());
    setPage(1);
  };

  const myUsername = mounted && isAuthenticated ? currentUser?.username : undefined;
  const showingMine = !!myUsername && username === myUsername;

  const hasFilters = statusFilter !== "all" || !!username || !!problem;
  const clearAll = () => {
    setStatusFilter("all");
    setUsername("");
    setUsernameInput("");
    setProblem(null);
    setPage(1);
  };

  const handlePrev = useCallback(() => setPage((p) => Math.max(1, p - 1)), []);
  const handleNext = useCallback(() => setPage((p) => p + 1), []);
  const hasMore = submissions.length === PAGE_SIZE;

  const userLabel = (userId: number) => {
    if (currentUser && mounted && userId === currentUser.id) return currentUser.username;
    if (username) return username;
    return `User #${userId}`;
  };

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
        className="mb-6 rounded-xl border border-border bg-card p-4 space-y-4"
      >
        <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-foreground-subtle">Problem</label>
            <ProblemPicker
              canSearch={mounted && isAuthenticated}
              selected={problem}
              onSelect={(p) => { setProblem(p); setPage(1); }}
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-foreground-subtle">
              Username <span className="font-normal">(exact, press Enter)</span>
            </label>
            {username ? (
              <div className="flex h-9 items-center gap-2 rounded-lg border border-primary/40 bg-primary/10 px-3 text-sm">
                <UserIcon className="h-4 w-4 shrink-0 text-primary" />
                <span className="truncate">{username}</span>
                <button
                  type="button"
                  onClick={() => { setUsername(""); setUsernameInput(""); setPage(1); }}
                  className="ml-auto shrink-0 rounded p-0.5 text-foreground-muted hover:text-foreground hover:bg-card"
                  aria-label="Clear username filter"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              <form
                onSubmit={(e) => { e.preventDefault(); applyUsername(usernameInput); }}
                className="relative"
              >
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-muted" />
                <Input
                  placeholder="e.g. mohamed_22"
                  value={usernameInput}
                  onChange={(e) => setUsernameInput(e.target.value)}
                  onBlur={() => usernameInput.trim() && applyUsername(usernameInput)}
                  className="pl-9 h-9"
                />
              </form>
            )}
          </div>

          <div className="flex items-end gap-2">
            {myUsername && (
              <Button
                size="sm"
                variant={showingMine ? "default" : "secondary"}
                className="h-9"
                onClick={() => {
                  if (showingMine) { setUsername(""); setUsernameInput(""); }
                  else { setUsername(myUsername); setUsernameInput(myUsername); }
                  setPage(1);
                }}
              >
                <UserIcon className="h-4 w-4" />
                My submissions
              </Button>
            )}
            {hasFilters && (
              <Button size="sm" variant="ghost" className="h-9" onClick={clearAll}>
                <X className="h-4 w-4" />
                Clear
              </Button>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {ALL_VERDICTS.map((v) => (
            <Button
              key={v.value}
              size="sm"
              variant={statusFilter === v.value ? "default" : "secondary"}
              onClick={() => { setStatusFilter(v.value); setPage(1); }}
              className="text-xs px-3 h-7"
            >
              {v.label}
            </Button>
          ))}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className={cn(
          "rounded-xl border border-border bg-card overflow-hidden transition-opacity",
          isFetching && !isLoading && "opacity-60",
        )}
      >
        <div className={cn(ROW_GRID, "px-6 py-3 text-xs font-medium text-foreground-subtle uppercase tracking-wider border-b border-border bg-card-elevated")}>
          <div className="hidden sm:block">#</div>
          <div>Problem</div>
          <div className="hidden sm:block">User</div>
          <div className="text-center">Verdict</div>
          <div className="text-right hidden sm:block">Time</div>
          <div className="text-right hidden sm:block">Memory</div>
          <div className="text-right">When</div>
        </div>

        {isLoading ? (
          <div className="p-4"><TableSkeleton columns={5} rows={5} /></div>
        ) : isError ? (
          <ErrorState title="Failed to load submissions" onRetry={() => refetch()} />
        ) : submissions.length === 0 ? (
          <EmptyState
            title="No submissions"
            description={
              username
                ? `No submissions found for user "${username}". Usernames must match exactly.`
                : "No submissions match your filters."
            }
            action={hasFilters ? <Button size="sm" variant="secondary" onClick={clearAll}>Clear filters</Button> : undefined}
          />
        ) : (
          submissions.map((submission) => {
            const isMine = mounted && currentUser?.id === submission.user_id;
            const name = problemNames.get(submission.problem_id);
            return (
              <div
                key={submission.id}
                className={cn(ROW_GRID, "px-6 py-3 border-b border-border/50 last:border-b-0 text-sm hover:bg-card-hover transition-colors")}
              >
                <div className="hidden sm:block font-mono text-xs">
                  {isMine ? (
                    <Link href={`/submissions/${submission.id}`} className="text-primary hover:underline">
                      {submission.id}
                    </Link>
                  ) : (
                    <span className="text-foreground-subtle">{submission.id}</span>
                  )}
                </div>
                <div className="min-w-0 flex items-center gap-2">
                  <Link
                    href={`/problems/${submission.problem_id}`}
                    className="truncate font-medium hover:text-primary transition-colors"
                    title={name}
                  >
                    {name ?? `Problem #${submission.problem_id}`}
                  </Link>
                  {problem?.id !== submission.problem_id && (
                    <button
                      type="button"
                      onClick={() => { setProblem({ id: submission.problem_id, name }); setPage(1); }}
                      className="shrink-0 rounded p-1 text-foreground-subtle hover:text-foreground hover:bg-card"
                      title="Show only this problem"
                      aria-label="Filter by this problem"
                    >
                      <Search className="h-3 w-3" />
                    </button>
                  )}
                </div>
                <div className={cn("hidden sm:block truncate", isMine ? "text-primary font-medium" : "text-foreground-muted")}>
                  {userLabel(submission.user_id)}
                  {isMine && <span className="ml-1 text-xs text-foreground-subtle font-normal">(you)</span>}
                </div>
                <div className="flex justify-center">
                  {isMine ? (
                    <Link href={`/submissions/${submission.id}`} title="View submission">
                      <VerdictBadge status={submission.verdict || "in_queue"} />
                    </Link>
                  ) : (
                    <VerdictBadge status={submission.verdict || "in_queue"} />
                  )}
                </div>
                <div className="text-right text-foreground-muted tabular-nums hidden sm:block">
                  {formatExecutionTime(submission.execution_time)}
                </div>
                <div className="text-right text-foreground-muted tabular-nums hidden sm:block">
                  {formatMemory(submission.execution_memory)}
                </div>
                <div
                  className="text-right text-xs text-foreground-subtle"
                  title={mounted ? formatDateTime(submission.submitted_at) : undefined}
                >
                  {mounted ? formatRelativeTime(submission.submitted_at) : "—"}
                </div>
              </div>
            );
          })
        )}
      </motion.div>

      <div className="flex items-center justify-center gap-4 mt-6">
        <Button size="sm" variant="outline" onClick={handlePrev} disabled={page <= 1}>
          <ChevronLeft className="h-4 w-4" />
          Previous
        </Button>
        <span className="text-sm text-foreground-muted">Page {page}</span>
        <Button size="sm" variant="outline" onClick={handleNext} disabled={!hasMore}>
          Next
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
