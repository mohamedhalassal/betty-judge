import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), "MMM d, yyyy");
}

export function formatDateTime(date: string | Date): string {
  return format(new Date(date), "MMM d, yyyy HH:mm");
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

export function formatExecutionTime(ms: number | null | undefined): string {
  if (ms == null) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatMemory(kb: number | null | undefined): string {
  if (kb == null) return "—";
  if (kb < 1024) return `${kb} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

export function getVerdictColor(status: string): string {
  const colors: Record<string, string> = {
    "Accepted": "text-success",
    "Wrong Answer": "text-destructive",
    "Time Limit Exceeded": "text-warning",
    "Runtime Error": "text-destructive",
    "Compilation Error": "text-warning",
    "Memory Limit Exceeded": "text-warning",
    "Pending": "text-foreground-muted",
    "Running": "text-info",
  };
  return colors[status] || "text-foreground-muted";
}

export function getVerdictBgColor(status: string): string {
  const colors: Record<string, string> = {
    "Accepted": "bg-success-muted",
    "Wrong Answer": "bg-destructive-muted",
    "Time Limit Exceeded": "bg-warning-muted",
    "Runtime Error": "bg-destructive-muted",
    "Compilation Error": "bg-warning-muted",
    "Memory Limit Exceeded": "bg-warning-muted",
    "Pending": "bg-card-elevated",
    "Running": "bg-info-muted",
  };
  return colors[status] || "bg-card-elevated";
}

export function getVerdictShort(status: string): string {
  const shorts: Record<string, string> = {
    "Accepted": "AC",
    "Wrong Answer": "WA",
    "Time Limit Exceeded": "TLE",
    "Runtime Error": "RE",
    "Compilation Error": "CE",
    "Memory Limit Exceeded": "MLE",
    "Pending": "...",
    "Running": "...",
  };
  return shorts[status] || status;
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen) + "...";
}
