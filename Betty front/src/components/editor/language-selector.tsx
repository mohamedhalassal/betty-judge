"use client";

import { useEditorStore } from "@/lib/store/editor-store";
import { languages } from "@/config/editor";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";

interface LanguageSelectorProps {
  className?: string;
}

export function LanguageSelector({ className }: LanguageSelectorProps) {
  const { language, setLanguage } = useEditorStore();

  return (
    <div className={cn("relative", className)}>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="appearance-none bg-card-elevated border border-border rounded-lg px-3 py-1.5 pr-8 text-sm font-medium text-foreground cursor-pointer hover:border-border-hover focus:outline-none focus:ring-2 focus:ring-ring/50 transition-colors"
      >
        {languages.map((lang) => (
          <option key={lang.id} value={lang.id}>
            {lang.name}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-foreground-muted pointer-events-none" />
    </div>
  );
}
