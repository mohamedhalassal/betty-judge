"use client";

import { use } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Calendar, CheckCircle2, Code2, BarChart3, Trophy } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { formatDate, formatRelativeTime } from "@/lib/utils";
import { useProfile } from "@/lib/hooks/use-users";
import { TableSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";

interface PageProps {
  params: Promise<{ username: string }>;
}

export default function ProfilePage({ params }: PageProps) {
  const { username } = use(params);
  const { data: profile, isLoading, isError, refetch } = useProfile(username);

  if (isLoading) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <TableSkeleton />
      </div>
    );
  }

  if (isError || !profile) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <ErrorState title="Failed to load profile" onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-start gap-6">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-white text-2xl font-bold shadow-lg shadow-primary/20">
            {profile.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-2xl font-bold">{profile.username}</h1>
            <div className="flex items-center gap-2 mt-1 text-sm text-foreground-muted">
              <Calendar className="h-4 w-4" />
              Joined {formatDate(profile.created_at)}
            </div>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
      >
        {[
          {
            label: "Problems Solved",
            value: profile.problems_solved,
            icon: CheckCircle2,
            color: "text-success",
          },
          {
            label: "Submissions",
            value: profile.total_submissions,
            icon: Code2,
            color: "text-primary",
          },
          {
            label: "Acceptance Rate",
            value: `${profile.acceptance_rate}%`,
            icon: BarChart3,
            color: "text-accent",
          },
          { label: "Rank", value: "#42", icon: Trophy, color: "text-warning" },
        ].map((s) => (
          <Card
            key={s.label}
            className="bg-card-elevated hover:bg-card-hover transition-colors"
          >
            <CardContent className="p-5">
              <div className="flex items-center gap-2 text-xs text-foreground-subtle mb-2">
                <s.icon className={`h-4 w-4 ${s.color}`} />
                {s.label}
              </div>
              <div className="text-2xl font-bold">{s.value}</div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      <div className="grid md:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardContent className="p-6">
              <h2 className="text-base font-semibold mb-4">Solved Problems</h2>
              <div className="space-y-2">
                {(profile.solved_problems || []).map(
                  (p: { id: number; name: string }) => (
                    <Link
                      key={p.id}
                      href={`/problems/${p.id}`}
                      className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-card-elevated transition-colors group"
                    >
                      <span className="text-sm group-hover:text-primary transition-colors">
                        {p.id}. {p.name}
                      </span>
                      <CheckCircle2 className="h-4 w-4 text-success" />
                    </Link>
                  ),
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
        >
          <Card>
            <CardContent className="p-6">
              <h2 className="text-base font-semibold mb-4">
                Recent Submissions
              </h2>
              <div className="space-y-2">
                {(profile.recent_submissions || []).map(
                  (s: {
                    id: number;
                    problem_id: number;
                    problem_name: string;
                    verdict: string;
                    submitted_at: string;
                  }) => (
                    <Link
                      key={s.id}
                      href={`/submissions/${s.id}`}
                      className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-card-elevated transition-colors group"
                    >
                      <div>
                        <span className="text-sm group-hover:text-primary transition-colors">
                          {s.problem_name}
                        </span>
                        <div className="text-xs text-foreground-subtle mt-0.5">
                          {formatRelativeTime(s.submitted_at)}
                        </div>
                      </div>
                      <VerdictBadge status={s.verdict} />
                    </Link>
                  ),
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
