"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeft, Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/shared/page-header";
import { useCreateProblem } from "@/lib/hooks/use-problems";
import Link from "next/link";

export default function CreateProblemPage() {
  const router = useRouter();
  const createMutation = useCreateProblem();

  const [form, setForm] = useState({
    name: "",
    statement: "",
    time_limit: 1000,
    memory_limit: 256,
    solution: "",
    checker_code: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.statement.trim()) return;

    createMutation.mutate(
      {
        name: form.name.trim(),
        statement: form.statement.trim(),
        time_limit: form.time_limit,
        memory_limit: form.memory_limit,
        solution: form.solution.trim() || null,
        checker_code: form.checker_code.trim() || null,
      },
      {
        onSuccess: (problem) => {
          router.push(`/problems/${problem.id}`);
        },
      },
    );
  };

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader title="Create Problem">
        <Button asChild variant="outline" size="sm">
          <Link href="/problems">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Link>
        </Button>
      </PageHeader>

      <motion.form
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        onSubmit={handleSubmit}
        className="space-y-6"
      >
        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Name</label>
              <Input
                placeholder="Two Sum"
                value={form.name}
                onChange={set("name")}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Statement</label>
              <textarea
                placeholder="# Problem Title&#10;&#10;Describe the problem here..."
                value={form.statement}
                onChange={set("statement")}
                required
                rows={12}
                className="flex w-full rounded-lg border border-input-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-primary transition-colors duration-200 font-mono"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Time Limit (ms)
                </label>
                <Input
                  type="number"
                  min={100}
                  max={10000}
                  value={form.time_limit}
                  onChange={set("time_limit")}
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Memory Limit (MB)
                </label>
                <Input
                  type="number"
                  min={16}
                  max={1024}
                  value={form.memory_limit}
                  onChange={set("memory_limit")}
                  required
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Optional</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Solution Code</label>
              <textarea
                placeholder="// Reference solution..."
                value={form.solution}
                onChange={set("solution")}
                rows={6}
                className="flex w-full rounded-lg border border-input-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-primary transition-colors duration-200 font-mono"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Checker Code</label>
              <textarea
                placeholder="// Custom checker (if any)..."
                value={form.checker_code}
                onChange={set("checker_code")}
                rows={6}
                className="flex w-full rounded-lg border border-input-border bg-input px-3 py-2 text-sm text-foreground placeholder:text-foreground-subtle focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-primary transition-colors duration-200 font-mono"
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="gradient"
            disabled={createMutation.isPending || !form.name.trim() || !form.statement.trim()}
          >
            {createMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Create Problem
              </>
            )}
          </Button>
        </div>
      </motion.form>
    </div>
  );
}
