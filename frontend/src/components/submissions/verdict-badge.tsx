"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface VerdictBadgeProps {
  status: string | null;
  showFull?: boolean;
  className?: string;
}

export function VerdictBadge({ status, showFull = false, className }: VerdictBadgeProps) {
  if (!status || status === "in_queue") {
    return (
      <Badge variant="outline" className={cn("animate-pulse", className)}>
        In Queue
      </Badge>
    );
  }

  const variantMap: Record<string, "success" | "destructive" | "warning" | "info" | "outline"> = {
    "accepted": "success",
    "wrong_answer": "destructive",
    "time_limit_exceeded": "warning",
  };

  const shortMap: Record<string, string> = {
    "accepted": "AC",
    "wrong_answer": "WA",
    "time_limit_exceeded": "TLE",
    "in_queue": "Q",
  };

  const formattedStatus = status.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
  const variant = variantMap[status] || "outline";
  const label = showFull ? formattedStatus : (shortMap[status] || formattedStatus);

  return (
    <Badge variant={variant} className={cn(className)}>
      {label}
    </Badge>
  );
}
