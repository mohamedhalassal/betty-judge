export interface Language {
  id: string;
  name: string;
  monacoId: string;
  defaultCode: string;
}

export const languages: Language[] = [
  {
    id: "cpp",
    name: "C++",
    monacoId: "cpp",
    defaultCode: `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    // Your solution here
    
    return 0;
}
`,
  },
  {
    id: "python",
    name: "Python",
    monacoId: "python",
    defaultCode: `import sys
input = sys.stdin.readline

def solve():
    # Your solution here
    pass

solve()
`,
  },
  {
    id: "java",
    name: "Java",
    monacoId: "java",
    defaultCode: `import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        // Your solution here
        
        br.close();
    }
}
`,
  },
];

export const editorDefaults = {
  fontSize: 14,
  tabSize: 4,
  theme: "betty-dark",
  minimap: false,
  wordWrap: "off" as const,
  lineNumbers: "on" as const,
  scrollBeyondLastLine: false,
  automaticLayout: true,
  padding: { top: 16, bottom: 16 },
  fontFamily: "'JetBrains Mono', monospace",
  fontLigatures: true,
  renderLineHighlight: "line" as const,
  cursorBlinking: "smooth" as const,
  cursorSmoothCaretAnimation: "on" as const,
  smoothScrolling: true,
};
