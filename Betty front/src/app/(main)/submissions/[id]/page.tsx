"use client";

import { use } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import {
  ArrowLeft,
  Clock,
  Calendar,
  Code2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/shared/error-state";
import {
  formatExecutionTime,
  formatDateTime,
} from "@/lib/utils";
import { useSubmission } from "@/lib/hooks/use-submissions";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => <Skeleton className="h-[400px] w-full" />,
});

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function SubmissionDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const submissionId = parseInt(id, 10);
  const { data: submission, isLoading, isError, refetch } = useSubmission(submissionId);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    );
  }

  if (isError || !submission) {
    return (
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
        <ErrorState title="Failed to load submission" onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="mb-6"
      >
        <Button asChild variant="ghost" size="sm">
          <Link href="/submissions">
            <ArrowLeft className="h-4 w-4" />
            Back to Submissions
          </Link>
        </Button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="mb-8"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-3">
              Submission #{submission.id}
              <VerdictBadge status={submission.verdict || "in_queue"} showFull />
            </h1>
            <div className="flex items-center gap-2 mt-2">
              <Link
                href={`/problems/${submission.problem_id}`}
                className="text-primary hover:underline text-sm font-medium"
              >
                Problem #{submission.problem_id}
              </Link>
            </div>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8"
      >
        {[
          {
            label: "Verdict",
            value: (submission.verdict || "in_queue").replace(/_/g, " "),
            icon: Code2,
            color: submission.verdict === "accepted" ? "text-success" : (submission.verdict === "in_queue" ? "text-foreground-muted" : "text-destructive"),
          },
          {
            label: "Runtime",
            value: formatExecutionTime(submission.execution_time),
            icon: Clock,
            color: "text-accent",
          },
          {
            label: "Submitted",
            value: formatDateTime(submission.submitted_at),
            icon: Calendar,
            color: "text-foreground-muted",
          },
        ].map((stat) => (
          <Card key={stat.label} className="bg-card-elevated border-border">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-xs text-foreground-subtle mb-1">
                <stat.icon className="h-3.5 w-3.5" />
                {stat.label}
              </div>
              <div className={`text-sm font-semibold capitalize ${stat.color}`}>
                {stat.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
      >
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Source Code</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg overflow-hidden border border-border">
              <MonacoEditor
                height="400px"
                language="cpp"
                value={submission.source_code}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  fontFamily: "'JetBrains Mono', monospace",
                  lineNumbers: "on",
                  scrollBeyondLastLine: false,
                  padding: { top: 16, bottom: 16 },
                  renderLineHighlight: "none",
                  automaticLayout: true,
                }}
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
