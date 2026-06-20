import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, formatDistanceToNow } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function toUtcDate(date: string | Date): Date {
  if (date instanceof Date) return date;
  const hasTimezone = date.endsWith("Z") || /[+\-]\d{2}:\d{2}$/.test(date);
  return new Date(hasTimezone ? date : date + "Z");
}

export function formatDate(date: string | Date): string {
  return format(toUtcDate(date), "MMM d, yyyy");
}

export function formatDateTime(date: string | Date): string {
  return format(toUtcDate(date), "MMM d, yyyy HH:mm");
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(toUtcDate(date), { addSuffix: true });
}

export function formatExecutionTime(ms: number | null | undefined): string {
  if (ms == null) return "\u2014";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatMemory(kb: number | null | undefined): string {
  if (kb == null) return "\u2014";
  if (kb < 1024) return `${kb} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

export function getVerdictColor(status: string): string {
  const colors: Record<string, string> = {
    accepted: "text-success",
    wrong_answer: "text-destructive",
    time_limit_exceeded: "text-warning",
    runtime_error: "text-destructive",
    compile_error: "text-destructive",
    memory_limit_exceeded: "text-warning",
    idleness_limit_exceeded: "text-warning",
    failed: "text-destructive",
    in_queue: "text-foreground-muted",
  };
  return colors[status] || "text-foreground-muted";
}

export function getVerdictBgColor(status: string): string {
  const colors: Record<string, string> = {
    accepted: "bg-success-muted",
    wrong_answer: "bg-destructive-muted",
    time_limit_exceeded: "bg-warning-muted",
    runtime_error: "bg-destructive-muted",
    compile_error: "bg-destructive-muted",
    memory_limit_exceeded: "bg-warning-muted",
    idleness_limit_exceeded: "bg-warning-muted",
    failed: "bg-destructive-muted",
    in_queue: "bg-card-elevated",
  };
  return colors[status] || "bg-card-elevated";
}

export function getVerdictShort(status: string): string {
  const shorts: Record<string, string> = {
    accepted: "AC",
    wrong_answer: "WA",
    time_limit_exceeded: "TLE",
    runtime_error: "RTE",
    compile_error: "CE",
    memory_limit_exceeded: "MLE",
    idleness_limit_exceeded: "ILE",
    failed: "FAIL",
    in_queue: "...",
  };
  return shorts[status] || status;
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen) + "...";
}
