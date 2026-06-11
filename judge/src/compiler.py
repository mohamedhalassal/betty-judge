import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompileResult:
    success: bool
    exe_file: Path | None = None
    message: str | None = None


def normalize_source_code(source_code: str) -> str:
    return (
        source_code.replace("\ufeff", "")
        .replace("\u00a0", " ")
        .replace("\u2007", " ")
        .replace("\u202f", " ")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\u200e", "")
        .replace("\u200f", "")
    )
def compile_cpp(source_code: str, temp_path: Path) -> CompileResult:
    source_file = temp_path / "main.cpp"
    exe_file = temp_path / "main"
    # write given source code to file
    source_code = normalize_source_code(source_code)
    source_file.write_text(source_code)
    # compile
    compile_result = subprocess.run(
        [
            "g++",
            "-std=gnu++20",
            "-O2",
            "-DONLINE_JUDGE",
            str(source_file),
            "-o",
            str(exe_file),
        ],
        capture_output=True,
        text=True,
    )
    if compile_result.returncode != 0:
        return CompileResult(
            success=False,
            message=f"Compile error: {compile_result.stderr}",
        )

    return CompileResult(
        success=True,
        exe_file=exe_file,
    )