"use client";

import { Badge } from "@/components/ui/badge";
import { getVerdictShort } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface VerdictBadgeProps {
  status: string | null;
  showFull?: boolean;
  className?: string;
}

export function VerdictBadge({ status, showFull = false, className }: VerdictBadgeProps) {
  if (!status) {
    return (
      <Badge variant="outline" className={cn("animate-pulse", className)}>
        Pending
      </Badge>
    );
  }

  const variantMap: Record<string, "success" | "destructive" | "warning" | "info" | "outline"> = {
    "Accepted": "success",
    "Wrong Answer": "destructive",
    "Time Limit Exceeded": "warning",
    "Runtime Error": "destructive",
    "Compilation Error": "warning",
    "Memory Limit Exceeded": "warning",
    "Pending": "outline",
    "Running": "info",
  };

  const variant = variantMap[status] || "outline";
  const label = showFull ? status : getVerdictShort(status);

  return (
    <Badge variant={variant} className={cn(className)}>
      {status === "Running" && (
        <span className="mr-1 inline-block h-2 w-2 rounded-full bg-current animate-pulse" />
      )}
      {label}
    </Badge>
  );
}
