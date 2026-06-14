"use client";

import { useState, use } from "react";
import { motion } from "framer-motion";
import {
  Send,
  RotateCcw,
  Maximize2,
  Minimize2,
  Clock,
  ChevronRight,
  FlaskConical,
  Plus,
  Trash2,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CodeEditor } from "@/components/editor/code-editor";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { ProblemDetailSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { useEditorStore } from "@/lib/store/editor-store";
import { useProblem } from "@/lib/hooks/use-problems";
import { useSubmitCode, useMySubmissions } from "@/lib/hooks/use-submissions";
import { useTestCases, useCreateTestCase, useDeleteTestCase } from "@/lib/hooks/use-test-cases";
import { cn, formatExecutionTime } from "@/lib/utils";
import Link from "next/link";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function ProblemDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const problemId = parseInt(id, 10);
  const [activeTab, setActiveTab] = useState<"description" | "submissions" | "test-cases">(
    "description",
  );
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [newTestCase, setNewTestCase] = useState({ input_data: "", expected_output: "", is_sample: false });
  const { getCode, resetCode, language } = useEditorStore();

  const { data: problem, isLoading, isError, refetch } = useProblem(problemId);
  const submitMutation = useSubmitCode();
  const { data: testCases, isLoading: tcLoading } = useTestCases(problemId);
  const createTcMutation = useCreateTestCase(problemId);
  const deleteTcMutation = useDeleteTestCase(problemId);

  const { data: submissions } = useMySubmissions();
  const problemSubmissions = submissions?.filter(
    (s) => s.problem_id === problemId,
  );

  const handleAddTestCase = () => {
    if (!newTestCase.input_data.trim() || !newTestCase.expected_output.trim()) return;
    createTcMutation.mutate(
      {
        input_data: newTestCase.input_data,
        expected_output: newTestCase.expected_output,
        is_sample: newTestCase.is_sample,
      },
      {
        onSuccess: () => {
          setNewTestCase({ input_data: "", expected_output: "", is_sample: false });
        },
      },
    );
  };

  const handleSubmit = () => {
    const currentCode = getCode(id);
    if (!currentCode) return;
    submitMutation.mutate(
      {
        problem_id: problemId,
        source_code: currentCode,
      },
      {
        onSuccess: () => {
          setActiveTab("submissions");
        },
      },
    );
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <ProblemDetailSkeleton />
      </div>
    );
  }

  if (isError || !problem) {
    return (
      <div className="p-8">
        <ErrorState title="Failed to load problem" onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div
      className={cn(
        "grid grid-cols-1 lg:grid-cols-2 grid-rows-[auto_1fr] min-h-[calc(100vh-4rem)]",
        isFullscreen && "fixed inset-0 z-50 bg-background !flex flex-col",
      )}
    >
      <div
        className={cn(
          "grid grid-cols-1 lg:grid-cols-subgrid col-span-1 lg:col-span-2 border-b border-border bg-card-elevated",
          isFullscreen && "hidden",
        )}
      >
        <div className="flex items-center gap-1 px-4 py-2 border-b lg:border-b-0 lg:border-r border-border">
          {(["description", "submissions", "test-cases"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                "px-4 py-2 text-sm font-medium rounded-lg transition-colors capitalize",
                activeTab === tab
                  ? "bg-card text-foreground"
                  : "text-foreground-muted hover:text-foreground hover:bg-card",
              )}
            >
              {tab}
            </button>
          ))}
          <Link
            href={`/problems/${id}/test-cases`}
            className="px-4 py-2 text-sm font-medium rounded-lg transition-colors text-foreground-muted hover:text-foreground hover:bg-card flex items-center gap-1.5"
          >
            <FlaskConical className="h-3.5 w-3.5" />
            Test Cases
          </Link>
        </div>

        <div className="flex items-center justify-between px-4 py-2">
          <div className="flex items-center gap-1">
            <Button
              size="icon-sm"
              variant="ghost"
              onClick={() => resetCode(id)}
              title="Reset code"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
            <Button
              size="icon-sm"
              variant="ghost"
              onClick={() => setIsFullscreen(!isFullscreen)}
              title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
            >
              {isFullscreen ? (
                <Minimize2 className="h-4 w-4" />
              ) : (
                <Maximize2 className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </div>

      <div
        className={cn(
          "grid grid-cols-1 lg:grid-cols-subgrid col-span-1 lg:col-span-2 overflow-hidden",
          isFullscreen && "!flex flex-col flex-1",
        )}
      >
        <div
          className={cn(
            "border-b lg:border-b-0 lg:border-r border-border overflow-y-auto p-6",
            isFullscreen && "hidden",
          )}
        >
          {activeTab === "description" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <div className="mb-4">
                <h1 className="text-xl font-bold">
                  {problem.id}. {problem.name}
                </h1>
              </div>

              <div className="prose prose-invert prose-sm max-w-none mb-8">
                {problem.statement?.split("\n").map((line: string, i: number) => {
                  if (line.startsWith("### ")) {
                    return (
                      <h3 key={i} className="text-base font-semibold mt-6 mb-2">
                        {line.replace("### ", "")}
                      </h3>
                    );
                  }
                  if (line.startsWith("- ")) {
                    return (
                      <div
                        key={i}
                        className="flex items-start gap-2 ml-2 mb-1 text-sm text-foreground-muted"
                      >
                        <ChevronRight className="h-3.5 w-3.5 mt-0.5 shrink-0 text-primary" />
                        <span
                          dangerouslySetInnerHTML={{
                            __html: formatInlineCode(line.replace("- ", "")),
                          }}
                        />
                      </div>
                    );
                  }
                  if (line.trim() === "")
                    return <div key={i} className="h-3" />;
                  return (
                    <p
                      key={i}
                      className="text-sm text-foreground-muted leading-relaxed mb-2"
                      dangerouslySetInnerHTML={{
                        __html: formatInlineCode(line),
                      }}
                    />
                  );
                })}
              </div>
            </motion.div>
          )}

          {activeTab === "submissions" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              {problemSubmissions && problemSubmissions.length > 0 ? (
                <div className="space-y-4">
                  {problemSubmissions.map((sub) => (
                    <Card
                      key={sub.id}
                      className="p-4 bg-card-elevated border-border"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <VerdictBadge
                            status={sub.verdict || "in_queue"}
                            showFull
                          />
                          <div className="mt-2 text-xs text-foreground-muted">
                            Submitted at{" "}
                            {new Date(sub.submitted_at).toLocaleString()}
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-2 text-sm text-foreground-muted">
                          {sub.execution_time !== null && (
                            <span className="flex items-center gap-1">
                              <Clock className="h-3.5 w-3.5" />
                              {formatExecutionTime(sub.execution_time)}
                            </span>
                          )}
                          <Link
                            href={`/submissions/${sub.id}`}
                            className="text-xs text-primary hover:underline"
                          >
                            View Code
                          </Link>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <p className="text-foreground-muted text-sm">
                  You have no submissions for this problem yet.
                </p>
              )}
            </motion.div>
          )}

          {activeTab === "test-cases" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Test Cases</h2>
              </div>

              {tcLoading ? (
                <div className="space-y-3">
                  {[1, 2].map((i) => (
                    <div key={i} className="h-20 rounded-lg bg-card-elevated animate-pulse" />
                  ))}
                </div>
              ) : testCases && testCases.length > 0 ? (
                <div className="space-y-3 mb-6">
                  {testCases.map((tc) => (
                    <Card key={tc.id} className="p-4 bg-card-elevated border-border">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0 space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge variant={tc.is_sample ? "info" : "outline"} className="text-[10px]">
                              {tc.is_sample ? "Sample" : `#${tc.id}`}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <p className="text-[10px] text-foreground-subtle uppercase font-medium mb-1">Input</p>
                              <pre className="text-xs bg-card p-2 rounded border border-border overflow-x-auto max-h-20">{tc.input_data}</pre>
                            </div>
                            <div>
                              <p className="text-[10px] text-foreground-subtle uppercase font-medium mb-1">Expected</p>
                              <pre className="text-xs bg-card p-2 rounded border border-border overflow-x-auto max-h-20">{tc.expected_output}</pre>
                            </div>
                          </div>
                        </div>
                        <Button
                          size="icon-sm"
                          variant="ghost"
                          onClick={() => deleteTcMutation.mutate(tc.id)}
                          className="shrink-0 text-destructive hover:bg-destructive-muted"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-foreground-muted mb-6">
                  No test cases yet. Add one below.
                </p>
              )}

              <div className="border-t border-border pt-4">
                <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Add Test Case
                </h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-foreground-subtle mb-1 block">Input Data</label>
                    <textarea
                      placeholder="2&#10;1 2&#10;3 4"
                      value={newTestCase.input_data}
                      onChange={(e) => setNewTestCase((p) => ({ ...p, input_data: e.target.value }))}
                      rows={3}
                      className="flex w-full rounded-lg border border-input-border bg-input px-3 py-2 text-xs text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-primary transition-colors font-mono"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-foreground-subtle mb-1 block">Expected Output</label>
                    <textarea
                      placeholder="3&#10;7"
                      value={newTestCase.expected_output}
                      onChange={(e) => setNewTestCase((p) => ({ ...p, expected_output: e.target.value }))}
                      rows={3}
                      className="flex w-full rounded-lg border border-input-border bg-input px-3 py-2 text-xs text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-primary transition-colors font-mono"
                    />
                  </div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={newTestCase.is_sample}
                      onChange={(e) => setNewTestCase((p) => ({ ...p, is_sample: e.target.checked }))}
                      className="rounded border-input-border"
                    />
                    <span className="text-xs text-foreground-muted">Sample case (shown to users)</span>
                  </label>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={handleAddTestCase}
                    disabled={createTcMutation.isPending || !newTestCase.input_data.trim() || !newTestCase.expected_output.trim()}
                  >
                    {createTcMutation.isPending ? (
                      <span className="h-3.5 w-3.5 border-2 border-foreground/30 border-t-foreground rounded-full animate-spin" />
                    ) : (
                      <Check className="h-3.5 w-3.5" />
                    )}
                    Add
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        <div className={cn("flex flex-col overflow-hidden", isFullscreen && "h-full")}>
          <div className="flex-1 min-h-[400px]">
            <CodeEditor problemId={id} height="100%" />
          </div>

          <div className="flex items-center justify-between px-4 py-3 border-t border-border bg-card">
            <div className="text-xs text-foreground-subtle">
              {language.toUpperCase()} • UTF-8
            </div>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="gradient"
                onClick={handleSubmit}
                disabled={submitMutation.isPending}
              >
                {submitMutation.isPending ? (
                  <>
                    <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Judging...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Submit
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatInlineCode(text: string): string {
  if (!text) return "";
  return text
    .replace(
      /\*\*(.*?)\*\*/g,
      "<strong class='text-foreground font-semibold'>$1</strong>",
    )
    .replace(
      /`(.*?)`/g,
      "<code class='px-1.5 py-0.5 rounded bg-card-elevated text-accent text-xs font-mono'>$1</code>",
    );
}
