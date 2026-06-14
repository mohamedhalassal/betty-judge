"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Plus, Trash2, FlaskConical, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/shared/page-header";
import { ErrorState } from "@/components/shared/error-state";
import { EmptyState } from "@/components/shared/empty-state";
import { useProblem } from "@/lib/hooks/use-problems";
import { useTestCases, useCreateTestCase, useDeleteTestCase } from "@/lib/hooks/use-test-cases";
import { toast } from "sonner";
import Link from "next/link";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function TestCasesPage({ params }: PageProps) {
  const { id } = use(params);
  const problemId = parseInt(id, 10);
  const router = useRouter();

  const { data: problem, isLoading: problemLoading, isError: problemError } = useProblem(problemId);
  const { data: testCases, isLoading, isError, refetch } = useTestCases(problemId);
  const createMutation = useCreateTestCase(problemId);
  const deleteMutation = useDeleteTestCase(problemId);

  const [inputData, setInputData] = useState("");
  const [expectedOutput, setExpectedOutput] = useState("");
  const [isSample, setIsSample] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputData.trim() || !expectedOutput.trim()) return;

    createMutation.mutate(
      { input_data: inputData, expected_output: expectedOutput, is_sample: isSample },
      {
        onSuccess: () => {
          setInputData("");
          setExpectedOutput("");
          setIsSample(false);
          toast.success("Test case added");
        },
        onError: () => toast.error("Failed to create test case"),
      },
    );
  };

  const handleDelete = (testCaseId: number) => {
    deleteMutation.mutate(testCaseId, {
      onSuccess: () => toast.success("Test case deleted"),
      onError: () => toast.error("Failed to delete test case"),
    });
  };

  if (problemLoading) {
    return <div className="mx-auto max-w-4xl px-4 py-8"><div className="h-8 w-48 bg-card-elevated rounded animate-pulse" /></div>;
  }

  if (problemError || !problem) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <ErrorState title="Problem not found" onRetry={() => router.push("/problems")} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link
          href={`/problems/${problemId}`}
          className="inline-flex items-center gap-1.5 text-sm text-foreground-muted hover:text-foreground transition-colors mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to problem
        </Link>
        <PageHeader
          title={`Test Cases - ${problem.name}`}
          description="Manage input/output test cases for this problem"
        />
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr_400px]">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FlaskConical className="h-5 w-5 text-primary" />
                Existing Test Cases
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-24 bg-card-elevated rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : isError ? (
                <ErrorState title="Failed to load test cases" onRetry={() => refetch()} />
              ) : !testCases || testCases.length === 0 ? (
                <EmptyState
                  title="No test cases"
                  description="Add test cases using the form on the right."
                />
              ) : (
                <div className="space-y-3">
                  {testCases.map((tc, index) => (
                    <motion.div
                      key={tc.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.03 }}
                      className="rounded-lg border border-border bg-card-elevated p-4"
                    >
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium text-foreground-muted">#{index + 1}</span>
                          {tc.is_sample && (
                            <span className="px-2 py-0.5 text-[10px] font-medium rounded-full bg-primary/10 text-primary border border-primary/20">
                              Sample
                            </span>
                          )}
                        </div>
                        <Button
                          size="icon-sm"
                          variant="ghost"
                          onClick={() => handleDelete(tc.id)}
                          disabled={deleteMutation.isPending}
                          className="text-destructive hover:bg-destructive-muted"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="text-xs font-medium text-foreground-subtle">Input:</span>
                          <pre className="mt-1 rounded bg-background p-2 text-xs font-mono overflow-x-auto">{tc.input_data}</pre>
                        </div>
                        <div>
                          <span className="text-xs font-medium text-foreground-subtle">Expected Output:</span>
                          <pre className="mt-1 rounded bg-background p-2 text-xs font-mono overflow-x-auto">{tc.expected_output}</pre>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Plus className="h-5 w-5 text-primary" />
                Add Test Case
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Input Data
                  </label>
                  <textarea
                    value={inputData}
                    onChange={(e) => setInputData(e.target.value)}
                    rows={4}
                    className="flex w-full rounded-lg border border-input-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-primary transition-colors duration-200 font-mono"
                    placeholder="Enter test input..."
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">
                    Expected Output
                  </label>
                  <textarea
                    value={expectedOutput}
                    onChange={(e) => setExpectedOutput(e.target.value)}
                    rows={4}
                    className="flex w-full rounded-lg border border-input-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-primary transition-colors duration-200 font-mono"
                    placeholder="Enter expected output..."
                    required
                  />
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isSample}
                    onChange={(e) => setIsSample(e.target.checked)}
                    className="rounded border-input-border bg-input text-primary focus:ring-primary/50 h-4 w-4"
                  />
                  <span className="text-sm text-foreground-muted">Sample test case (shown to users)</span>
                </label>
                <Button
                  type="submit"
                  variant="gradient"
                  className="w-full"
                  disabled={createMutation.isPending || !inputData.trim() || !expectedOutput.trim()}
                >
                  {createMutation.isPending ? (
                    <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <Plus className="h-4 w-4" />
                      Add Test Case
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
