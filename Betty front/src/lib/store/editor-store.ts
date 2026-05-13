import { create } from "zustand";
import { persist } from "zustand/middleware";
import { languages } from "@/config/editor";

interface EditorState {
  language: string;
  fontSize: number;
  theme: string;
  codes: Record<string, Record<string, string>>; // { [problemId]: { [lang]: code } }
  setLanguage: (lang: string) => void;
  setFontSize: (size: number) => void;
  setTheme: (theme: string) => void;
  getCode: (problemId: string) => string;
  setCode: (problemId: string, code: string) => void;
  resetCode: (problemId: string) => void;
}

export const useEditorStore = create<EditorState>()(
  persist(
    (set, get) => ({
      language: "cpp",
      fontSize: 14,
      theme: "betty-dark",
      codes: {},
      setLanguage: (language) => set({ language }),
      setFontSize: (fontSize) => set({ fontSize }),
      setTheme: (theme) => set({ theme }),
      getCode: (problemId) => {
        const { codes, language } = get();
        const langDefault = languages.find((l) => l.id === language);
        return codes[problemId]?.[language] || langDefault?.defaultCode || "";
      },
      setCode: (problemId, code) => {
        const { codes, language } = get();
        set({
          codes: {
            ...codes,
            [problemId]: {
              ...codes[problemId],
              [language]: code,
            },
          },
        });
      },
      resetCode: (problemId) => {
        const { codes, language } = get();
        const langDefault = languages.find((l) => l.id === language);
        set({
          codes: {
            ...codes,
            [problemId]: {
              ...codes[problemId],
              [language]: langDefault?.defaultCode || "",
            },
          },
        });
      },
    }),
    {
      name: "betty-editor",
      partialize: (state) => ({
        language: state.language,
        fontSize: state.fontSize,
        theme: state.theme,
        codes: state.codes,
      }),
    }
  )
);
