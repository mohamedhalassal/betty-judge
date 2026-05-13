"use client";

import dynamic from "next/dynamic";
import { useEditorStore } from "@/lib/store/editor-store";
import { editorDefaults } from "@/config/editor";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-card">
      <Skeleton className="w-full h-full" />
    </div>
  ),
});

interface CodeEditorProps {
  problemId: string;
  className?: string;
  height?: string;
}

export function CodeEditor({ problemId, className, height = "100%" }: CodeEditorProps) {
  const { language, fontSize, getCode, setCode } = useEditorStore();
  const code = getCode(problemId);

  const handleEditorMount = (editor: unknown, monaco: unknown) => {
    // @ts-expect-error - Monaco types
    monaco.editor.defineTheme("betty-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "comment", foreground: "6b7280", fontStyle: "italic" },
        { token: "keyword", foreground: "818cf8" },
        { token: "string", foreground: "34d399" },
        { token: "number", foreground: "f59e0b" },
        { token: "type", foreground: "22d3ee" },
        { token: "function", foreground: "67e8f9" },
      ],
      colors: {
        "editor.background": "#0e0e16",
        "editor.foreground": "#e4e4e7",
        "editor.lineHighlightBackground": "#1a1a2e",
        "editor.selectionBackground": "#6366f140",
        "editorCursor.foreground": "#6366f1",
        "editorLineNumber.foreground": "#3f3f5c",
        "editorLineNumber.activeForeground": "#71717a",
        "editor.inactiveSelectionBackground": "#6366f120",
        "editorIndentGuide.background": "#1e1e2e",
        "editorIndentGuide.activeBackground": "#2a2a3e",
        "editorWidget.background": "#12121a",
        "editorWidget.border": "#1e1e2e",
      },
    });
    // @ts-expect-error - Monaco types
    monaco.editor.setTheme("betty-dark");
  };

  return (
    <div className={cn("overflow-hidden rounded-lg border border-border", className)}>
      <MonacoEditor
        height={height}
        language={language === "cpp" ? "cpp" : language}
        value={code}
        onChange={(value) => setCode(problemId, value || "")}
        onMount={handleEditorMount}
        theme="betty-dark"
        options={{
          fontSize,
          tabSize: editorDefaults.tabSize,
          minimap: { enabled: false },
          wordWrap: editorDefaults.wordWrap,
          lineNumbers: editorDefaults.lineNumbers,
          scrollBeyondLastLine: editorDefaults.scrollBeyondLastLine,
          automaticLayout: true,
          padding: editorDefaults.padding,
          fontFamily: editorDefaults.fontFamily,
          fontLigatures: editorDefaults.fontLigatures,
          renderLineHighlight: editorDefaults.renderLineHighlight,
          cursorBlinking: editorDefaults.cursorBlinking,
          cursorSmoothCaretAnimation: editorDefaults.cursorSmoothCaretAnimation,
          smoothScrolling: editorDefaults.smoothScrolling,
          contextmenu: true,
          suggest: {
            showKeywords: true,
            showSnippets: true,
          },
        }}
      />
    </div>
  );
}
