"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/shared/page-header";

export default function LeaderboardPage() {
  const [search, setSearch] = useState("");

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

      <div className="rounded-xl border border-border bg-card overflow-hidden p-12 text-center">
        <p className="text-foreground-muted text-sm">
          Leaderboard coming soon.
        </p>
      </div>
    </div>
  );
}
