import { useEffect, useState } from "react";
import { format, formatDistanceToNow } from "date-fns";
import { toUtcDate } from "@/lib/utils";

export function useLocalTime(utcDate: string | Date, pattern = "MMM d, yyyy HH:mm"): string {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return "\u2014";

  return format(toUtcDate(utcDate), pattern);
}

export function useLocalRelativeTime(utcDate: string | Date): string {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return "\u2014";

  return formatDistanceToNow(toUtcDate(utcDate), { addSuffix: true });
}
