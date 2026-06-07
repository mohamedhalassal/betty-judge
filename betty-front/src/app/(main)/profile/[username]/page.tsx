"use client";

import { use } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Calendar, CheckCircle2, Code2, BarChart3, Trophy } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { VerdictBadge } from "@/components/submissions/verdict-badge";
import { formatDate, formatRelativeTime } from "@/lib/utils";

const mockProfile = {
  username: "coder42",
  created_at: "2025-06-15T00:00:00Z",
  problems_solved: 47,
  total_submissions: 152,
  acceptance_rate: 68.4,
  solved_problems: [
    { id: 1, name: "Two Sum" },
    { id: 3, name: "Longest Substring" },
    { id: 7, name: "Container With Most Water" },
    { id: 9, name: "Valid Parentheses" },
    { id: 10, name: "Merge Two Sorted Lists" },
    { id: 12, name: "Binary Tree Inorder" },
  ],
  recent_submissions: [
    { id: 1, problem_id: 1, problem_name: "Two Sum", status: "Accepted", submitted_at: "2026-05-12T10:30:00Z" },
    { id: 2, problem_id: 2, problem_name: "Add Two Numbers", status: "Wrong Answer", submitted_at: "2026-05-12T10:25:00Z" },
    { id: 3, problem_id: 3, problem_name: "Longest Substring", status: "TLE", submitted_at: "2026-05-12T09:45:00Z" },
    { id: 6, problem_id: 7, problem_name: "Container With Most Water", status: "Accepted", submitted_at: "2026-05-11T20:30:00Z" },
  ],
  activity: Array.from({ length: 365 }, (_, i) => ({
    date: new Date(Date.now() - (364 - i) * 86400000).toISOString().split("T")[0],
    count: Math.random() > 0.6 ? Math.floor(Math.random() * 8) : 0,
  })),
};

interface PageProps { params: Promise<{ username: string }>; }

export default function ProfilePage({ params }: PageProps) {
  const { username } = use(params);
  const profile = mockProfile;
  const maxActivity = Math.max(...profile.activity.map((a) => a.count), 1);

  const getColor = (count: number) => {
    if (count === 0) return "bg-card-elevated";
    const r = count / maxActivity;
    if (r > 0.75) return "bg-primary";
    if (r > 0.5) return "bg-primary/70";
    if (r > 0.25) return "bg-primary/40";
    return "bg-primary/20";
  };

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-start gap-6">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-white text-2xl font-bold shadow-lg shadow-primary/20">
            {profile.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-2xl font-bold">{profile.username}</h1>
            <div className="flex items-center gap-2 mt-1 text-sm text-foreground-muted">
              <Calendar className="h-4 w-4" />Joined {formatDate(profile.created_at)}
            </div>
          </div>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Problems Solved", value: profile.problems_solved, icon: CheckCircle2, color: "text-success" },
          { label: "Submissions", value: profile.total_submissions, icon: Code2, color: "text-primary" },
          { label: "Acceptance Rate", value: `${profile.acceptance_rate}%`, icon: BarChart3, color: "text-accent" },
          { label: "Rank", value: "#42", icon: Trophy, color: "text-warning" },
        ].map((s) => (
          <Card key={s.label} className="bg-card-elevated hover:bg-card-hover transition-colors">
            <CardContent className="p-5">
              <div className="flex items-center gap-2 text-xs text-foreground-subtle mb-2">
                <s.icon className={`h-4 w-4 ${s.color}`} />{s.label}
              </div>
              <div className="text-2xl font-bold">{s.value}</div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-8">
        <Card>
          <CardContent className="p-6">
            <h2 className="text-base font-semibold mb-4">Activity</h2>
            <div className="overflow-x-auto pb-2">
              <div className="flex gap-[3px]" style={{ minWidth: "max-content" }}>
                {Array.from({ length: 52 }).map((_, w) => (
                  <div key={w} className="flex flex-col gap-[3px]">
                    {Array.from({ length: 7 }).map((_, d) => {
                      const a = profile.activity[w * 7 + d];
                      if (!a) return <div key={d} className="h-3 w-3" />;
                      return <div key={d} className={`h-3 w-3 rounded-sm ${getColor(a.count)}`} title={`${a.date}: ${a.count}`} />;
                    })}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid md:grid-cols-2 gap-8">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card><CardContent className="p-6">
            <h2 className="text-base font-semibold mb-4">Solved Problems</h2>
            <div className="space-y-2">
              {profile.solved_problems.map((p) => (
                <Link key={p.id} href={`/problems/${p.id}`} className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-card-elevated transition-colors group">
                  <span className="text-sm group-hover:text-primary transition-colors">{p.id}. {p.name}</span>
                  <CheckCircle2 className="h-4 w-4 text-success" />
                </Link>
              ))}
            </div>
          </CardContent></Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <Card><CardContent className="p-6">
            <h2 className="text-base font-semibold mb-4">Recent Submissions</h2>
            <div className="space-y-2">
              {profile.recent_submissions.map((s) => (
                <Link key={s.id} href={`/submissions/${s.id}`} className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-card-elevated transition-colors group">
                  <div>
                    <span className="text-sm group-hover:text-primary transition-colors">{s.problem_name}</span>
                    <div className="text-xs text-foreground-subtle mt-0.5">{formatRelativeTime(s.submitted_at)}</div>
                  </div>
                  <VerdictBadge status={s.status} />
                </Link>
              ))}
            </div>
          </CardContent></Card>
        </motion.div>
      </div>
    </div>
  );
}
