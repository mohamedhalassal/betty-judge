"use client";

import { useState, use } from "react";
import { motion } from "framer-motion";
import {
  Play,
  Send,
  RotateCcw,
  Maximize2,
  Minimize2,
  Clock,
  HardDrive,
  ChevronRight,
  Copy,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { CodeEditor } from "@/components/editor/code-editor";
import { LanguageSelector } from "@/components/editor/language-selector";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { ProblemDetailSkeleton } from "@/components/shared/loading-skeleton";
import { useEditorStore } from "@/lib/store/editor-store";
import { cn, formatExecutionTime, formatMemory } from "@/lib/utils";
import Link from "next/link";

// Mock problem data
const mockProblem = {
  id: 1,
  name: "Two Sum",
  statement: `Given an array of integers \`nums\` and an integer \`target\`, return indices of the two numbers such that they add up to \`target\`.

You may assume that each input would have **exactly one solution**, and you may not use the same element twice.

You can return the answer in any order.

### Constraints

- \`2 <= nums.length <= 10^4\`
- \`-10^9 <= nums[i] <= 10^9\`
- \`-10^9 <= target <= 10^9\`
- Only one valid answer exists.`,
  difficulty: "Easy",
  tags: ["Array", "Hash Table"],
  time_limit: "1 second",
  memory_limit: "256 MB",
  test_cases: [
    { id: 1, input_data: "4\n2 7 11 15\n9", expected_output: "0 1", is_sample: true },
    { id: 2, input_data: "3\n3 2 4\n6", expected_output: "1 2", is_sample: true },
    { id: 3, input_data: "2\n3 3\n6", expected_output: "0 1", is_sample: true },
  ],
};

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function ProblemDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const [activeTab, setActiveTab] = useState<"description" | "submissions">("description");
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<{
    status: string;
    time: number;
    memory: number;
  } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const { resetCode, language } = useEditorStore();

  const problem = mockProblem; // Will use useProblem(id) when API is ready

  const handleSubmit = () => {
    setIsSubmitting(true);
    // Simulate submission
    setTimeout(() => {
      setSubmissionResult({
        status: "Accepted",
        time: 42,
        memory: 8400,
      });
      setIsSubmitting(false);
    }, 2000);
  };

  const handleCopy = (text: string, caseId: number) => {
    navigator.clipboard.writeText(text);
    setCopiedId(caseId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className={cn("flex flex-col lg:flex-row min-h-[calc(100vh-4rem)]", isFullscreen && "fixed inset-0 z-50 bg-background")}>
      {/* Left Panel — Problem Description */}
      <div className={cn("lg:w-1/2 border-r border-border overflow-y-auto", isFullscreen && "hidden")}>
        {/* Tabs */}
        <div className="sticky top-0 z-10 flex items-center gap-1 px-4 py-2 border-b border-border bg-card-elevated">
          {(["description", "submissions"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                "px-4 py-2 text-sm font-medium rounded-lg transition-colors capitalize",
                activeTab === tab
                  ? "bg-card text-foreground"
                  : "text-foreground-muted hover:text-foreground hover:bg-card"
              )}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === "description" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              {/* Problem Title */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-xl font-bold">
                    {problem.id}. {problem.name}
                  </h1>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="success" className="text-xs">{problem.difficulty}</Badge>
                    {problem.tags?.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">{tag}</Badge>
                    ))}
                  </div>
                </div>
              </div>

              {/* Time/Memory Limits */}
              <div className="flex items-center gap-4 mb-6 text-sm text-foreground-muted">
                <div className="flex items-center gap-1.5">
                  <Clock className="h-4 w-4" />
                  <span>{problem.time_limit}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <HardDrive className="h-4 w-4" />
                  <span>{problem.memory_limit}</span>
                </div>
              </div>

              {/* Statement */}
              <div className="prose prose-invert prose-sm max-w-none mb-8">
                {problem.statement.split("\n").map((line, i) => {
                  if (line.startsWith("### ")) {
                    return <h3 key={i} className="text-base font-semibold mt-6 mb-2">{line.replace("### ", "")}</h3>;
                  }
                  if (line.startsWith("- ")) {
                    return (
                      <div key={i} className="flex items-start gap-2 ml-2 mb-1 text-sm text-foreground-muted">
                        <ChevronRight className="h-3.5 w-3.5 mt-0.5 shrink-0 text-primary" />
                        <span dangerouslySetInnerHTML={{ __html: formatInlineCode(line.replace("- ", "")) }} />
                      </div>
                    );
                  }
                  if (line.trim() === "") return <div key={i} className="h-3" />;
                  return (
                    <p key={i} className="text-sm text-foreground-muted leading-relaxed mb-2" dangerouslySetInnerHTML={{ __html: formatInlineCode(line) }} />
                  );
                })}
              </div>

              {/* Sample Test Cases */}
              <div className="space-y-4">
                <h3 className="text-base font-semibold">Examples</h3>
                {problem.test_cases
                  .filter((tc) => tc.is_sample)
                  .map((tc, index) => (
                    <Card key={tc.id} className="overflow-hidden bg-card-elevated border-border">
                      <div className="px-4 py-2 bg-card border-b border-border">
                        <span className="text-xs font-medium text-foreground-muted">
                          Example {index + 1}
                        </span>
                      </div>
                      <div className="grid sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-border">
                        <div className="p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-foreground-subtle uppercase tracking-wide">Input</span>
                            <button
                              onClick={() => handleCopy(tc.input_data, tc.id)}
                              className="text-foreground-subtle hover:text-foreground transition-colors"
                            >
                              {copiedId === tc.id ? (
                                <Check className="h-3.5 w-3.5 text-success" />
                              ) : (
                                <Copy className="h-3.5 w-3.5" />
                              )}
                            </button>
                          </div>
                          <pre className="text-sm font-mono text-foreground-muted whitespace-pre-wrap">{tc.input_data}</pre>
                        </div>
                        <div className="p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-foreground-subtle uppercase tracking-wide">Output</span>
                            <button
                              onClick={() => handleCopy(tc.expected_output, tc.id + 1000)}
                              className="text-foreground-subtle hover:text-foreground transition-colors"
                            >
                              {copiedId === tc.id + 1000 ? (
                                <Check className="h-3.5 w-3.5 text-success" />
                              ) : (
                                <Copy className="h-3.5 w-3.5" />
                              )}
                            </button>
                          </div>
                          <pre className="text-sm font-mono text-foreground-muted whitespace-pre-wrap">{tc.expected_output}</pre>
                        </div>
                      </div>
                    </Card>
                  ))}
              </div>
            </motion.div>
          )}

          {activeTab === "submissions" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <p className="text-foreground-muted text-sm">
                Your submissions for this problem will appear here.
              </p>
            </motion.div>
          )}
        </div>
      </div>

      {/* Right Panel — Code Editor */}
      <div className={cn("lg:w-1/2 flex flex-col", isFullscreen && "w-full")}>
        {/* Editor Toolbar */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card-elevated">
          <div className="flex items-center gap-3">
            <LanguageSelector />
          </div>
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

        {/* Editor */}
        <div className="flex-1 min-h-[400px]">
          <CodeEditor problemId={id} height="100%" />
        </div>

        {/* Submission Result */}
        {submissionResult && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="px-4 py-3 border-t border-border bg-card-elevated"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <VerdictBadge status={submissionResult.status} showFull />
                <div className="flex items-center gap-4 text-sm text-foreground-muted">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {formatExecutionTime(submissionResult.time)}
                  </span>
                  <span className="flex items-center gap-1">
                    <HardDrive className="h-3.5 w-3.5" />
                    {formatMemory(submissionResult.memory)}
                  </span>
                </div>
              </div>
              <Link href={`/submissions/1`} className="text-xs text-primary hover:underline">
                View Details →
              </Link>
            </div>
          </motion.div>
        )}

        {/* Bottom Actions */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-border bg-card">
          <div className="text-xs text-foreground-subtle">
            {language.toUpperCase()} • UTF-8
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" variant="secondary" disabled={isSubmitting}>
              <Play className="h-4 w-4" />
              Run
            </Button>
            <Button
              size="sm"
              variant="gradient"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
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
  );
}

function formatInlineCode(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong class='text-foreground font-semibold'>$1</strong>")
    .replace(/`(.*?)`/g, "<code class='px-1.5 py-0.5 rounded bg-card-elevated text-accent text-xs font-mono'>$1</code>");
}
