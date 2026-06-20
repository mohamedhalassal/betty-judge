import { useEffect, useState } from "react";
import { format, formatDistanceToNow } from "date-fns";

export function useLocalTime(utcDate: string | Date, pattern = "MMM d, yyyy HH:mm"): string | null {
  const [display, setDisplay] = useState<string | null>(null);

  useEffect(() => {
    setDisplay(format(new Date(utcDate), pattern));
  }, [utcDate, pattern]);

  return display;
}

export function useLocalRelativeTime(utcDate: string | Date): string | null {
  const [display, setDisplay] = useState<string | null>(null);

  useEffect(() => {
    setDisplay(formatDistanceToNow(new Date(utcDate), { addSuffix: true }));
  }, [utcDate]);

  return display;
}
