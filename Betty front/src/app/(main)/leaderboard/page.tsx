"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search, Trophy, Medal } from "lucide-react";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/shared/page-header";
import { TableSkeleton } from "@/components/shared/loading-skeleton";
import { cn } from "@/lib/utils";
import { useLeaderboard } from "@/lib/hooks/use-users";

const rankColors: Record<number, string> = {
  1: "text-yellow-400",
  2: "text-zinc-300",
  3: "text-amber-600",
};

const rankBg: Record<number, string> = {
  1: "bg-yellow-400/10 border-yellow-400/20",
  2: "bg-zinc-300/10 border-zinc-300/20",
  3: "bg-amber-600/10 border-amber-600/20",
};

export default function LeaderboardPage() {
  const [search, setSearch] = useState("");
  const { data: response, isLoading } = useLeaderboard();

  const leaderboard = response?.items || [];
  const filtered = leaderboard.filter((u) =>
    u.username.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <PageHeader
        title="Leaderboard"
        description="Top competitive programmers on Betty Judge"
      >
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-subtle" />
          <Input
            placeholder="Search users..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </PageHeader>

      {isLoading ? (
        <TableSkeleton />
      ) : (
        <>
          {/* Top 3 Podium */}
          {leaderboard.length >= 3 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="grid grid-cols-3 gap-4 mb-8"
            >
              {[1, 0, 2].map((idx) => {
                const user = leaderboard[idx];
                if (!user) return null;
                const rank = idx === 0 ? 1 : idx === 1 ? 2 : 3;
                return (
                  <motion.div
                    key={user.username}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 + idx * 0.1 }}
                  >
                    <Link
                      href={`/profile/${user.username}`}
                      className={cn(
                        "flex flex-col items-center p-6 rounded-xl border transition-all hover:scale-[1.02]",
                        rankBg[rank] || "border-border bg-card",
                      )}
                    >
                      <div className={cn("text-2xl mb-2", rankColors[rank])}>
                        {rank === 1 ? (
                          <Trophy className="h-8 w-8" />
                        ) : (
                          <Medal className="h-7 w-7" />
                        )}
                      </div>
                      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent text-white font-bold text-lg mb-2">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <span className="font-semibold text-sm">
                        {user.username}
                      </span>
                      <span className="text-xs text-foreground-muted mt-1">
                        {user.problems_solved} solved
                      </span>
                    </Link>
                  </motion.div>
                );
              })}
            </motion.div>
          )}

          {/* Full Table */}
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="rounded-xl border border-border bg-card overflow-hidden"
          >
            <div className="grid grid-cols-[60px_1fr_100px_100px_100px] gap-4 px-6 py-3 text-xs font-medium text-foreground-subtle uppercase tracking-wider border-b border-border bg-card-elevated">
              <div className="text-center">Rank</div>
              <div>User</div>
              <div className="text-center">Solved</div>
              <div className="text-center hidden sm:block">Submissions</div>
              <div className="text-center">Acc. Rate</div>
            </div>
            {filtered.map((user, index) => {
              const displayRank = index + 1;
              return (
                <motion.div
                  key={user.username}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.03 }}
                >
                  <Link
                    href={`/profile/${user.username}`}
                    className={cn(
                      "grid grid-cols-[60px_1fr_100px_100px_100px] gap-4 px-6 py-4 items-center hover:bg-card-hover border-b border-border/50 transition-colors group",
                      displayRank <= 3 && rankBg[displayRank],
                    )}
                  >
                    <div
                      className={cn(
                        "text-center font-bold",
                        rankColors[displayRank] || "text-foreground-muted",
                      )}
                    >
                      #{displayRank}
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20 text-primary text-xs font-bold">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm font-medium group-hover:text-primary transition-colors">
                        {user.username}
                      </span>
                    </div>
                    <div className="text-center text-sm font-medium">
                      {user.problems_solved}
                    </div>
                    <div className="text-center text-sm text-foreground-muted hidden sm:block">
                      {user.total_submissions || 0}
                    </div>
                    <div className="text-center text-sm font-mono text-foreground-muted">
                      {user.acceptance_rate?.toFixed(1) || "0.0"}%
                    </div>
                  </Link>
                </motion.div>
              );
            })}
            {filtered.length === 0 && (
              <div className="p-8 text-center text-sm text-foreground-muted">
                No users found.
              </div>
            )}
          </motion.div>
        </>
      )}
    </div>
  );
}
