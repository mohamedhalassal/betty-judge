import Link from "next/link";
import { Zap, GitBranch } from "lucide-react";
import { Separator } from "@/components/ui/separator";

export function Footer() {
  return (
    <footer className="border-t border-border bg-background-secondary">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between py-6 gap-4">
          <div className="flex items-center gap-2 text-foreground-muted">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-gradient-to-br from-primary to-accent">
              <Zap className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-sm">
              © {new Date().getFullYear()} Betty Judge. All rights reserved.
            </span>
          </div>
          <div className="flex items-center gap-6">
            <Link
              href="/problems"
              className="text-sm text-foreground-subtle hover:text-foreground-muted transition-colors"
            >
              Problems
            </Link>
            <Link
              href="/leaderboard"
              className="text-sm text-foreground-subtle hover:text-foreground-muted transition-colors"
            >
              Leaderboard
            </Link>
            <Separator orientation="vertical" className="h-4" />
            <a
              href="https://github.com/betty-judge"
              target="_blank"
              rel="noopener noreferrer"
              className="text-foreground-subtle hover:text-foreground-muted transition-colors"
            >
              <GitBranch className="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
