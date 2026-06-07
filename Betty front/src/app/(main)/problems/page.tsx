"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search, Circle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/shared/page-header";
import { TableSkeleton } from "@/components/shared/loading-skeleton";
import { ErrorState } from "@/components/shared/error-state";
import { EmptyState } from "@/components/shared/empty-state";
import { useProblems } from "@/lib/hooks/use-problems";

export default function ProblemsPage() {
  const [search, setSearch] = useState("");

  const { data: problems, isLoading, isError, refetch } = useProblems(search || undefined);

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader
        title="Problems"
        description="Practice algorithmic challenges and sharpen your skills"
      />

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-3 mb-6"
      >
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-subtle" />
          <Input
            placeholder="Search problems..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-border bg-card overflow-hidden"
      >
        <div className="grid grid-cols-[48px_1fr_48px] gap-4 px-4 sm:px-6 py-3 text-xs font-medium text-foreground-subtle uppercase tracking-wider border-b border-border bg-card-elevated">
          <div className="text-center">#</div>
          <div>Title</div>
          <div className="text-center">Status</div>
        </div>

        {isLoading ? (
          <div className="p-4">
            <TableSkeleton columns={3} rows={5} />
          </div>
        ) : isError ? (
          <ErrorState
            title="Failed to load problems"
            onRetry={() => refetch()}
          />
        ) : !problems || problems.length === 0 ? (
          <EmptyState
            title="No problems found"
            description="Try adjusting your search query."
          />
        ) : (
          problems.map((problem, index) => (
            <motion.div
              key={problem.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.02 }}
            >
              <Link
                href={`/problems/${problem.id}`}
                className="grid grid-cols-[48px_1fr_48px] gap-4 px-4 sm:px-6 py-4 items-center hover:bg-card-hover border-b border-border/50 transition-colors duration-150 group"
              >
                <div className="text-center text-sm text-foreground-muted">
                  {problem.id}
                </div>
                <div>
                  <span className="text-sm font-medium group-hover:text-primary transition-colors">
                    {problem.name}
                  </span>
                </div>
                <div className="flex justify-center">
                  <Circle className="h-5 w-5 text-foreground-subtle/30" />
                </div>
              </Link>
            </motion.div>
          ))
        )}
      </motion.div>
    </div>
  );
}
