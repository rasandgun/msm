import subprocess
import os
from typing import List, Optional

LANGUAGE_COMMANDS = {
    "cpp":   ("g++", ["{src}", "-o", "{out}"], "{out}"),
    "java":  ("javac", ["-d", "{dir}", "{src}"], ["java", "-cp", "{dir}", "{name}"]),
    "py":    (None, None, ["python3", "{src}"]),
    "pas":   ("fpc", ["{src}", "-o{out}"], "{out}"),
    "rs":    ("rustc", ["{src}", "-o", "{out}"], "{out}"),
    "kt":    ("kotlinc", ["{src}", "-d", "{dir}"], ["kotlin", "{name}Kt"]),
    "d":     ("dmd", ["{src}", "-of{out}"], "{out}"),
    "js":    (None, None, ["node", "{src}"]),
    "rb":    (None, None, ["ruby", "{src}"]),
}

def compile_program(src_path: str, work_dir: Optional[str] = None) -> list[str]:
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"File not found: {src_path}")
    ext = os.path.splitext(src_path)[1][1:].lower()
    if ext not in LANGUAGE_COMMANDS:
        raise ValueError(f"Unsupported extension: .{ext}")
    compiler, comp_args_template, run_template = LANGUAGE_COMMANDS[ext]
    name = os.path.splitext(os.path.basename(src_path))[0]
    out_path = os.path.join(work_dir or os.path.dirname(src_path), f"msm_{name}")
    if compiler:
        comp_args = [arg.format(src=src_path, out=out_path, dir=os.path.dirname(src_path), name=name) for arg in comp_args_template]
        res = subprocess.run([compiler] + comp_args, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Compilation error:\n{res.stderr or res.stdout}")
    if isinstance(run_template, list):
        return [arg.format(src=src_path, out=out_path, dir=os.path.dirname(src_path), name=name) for arg in run_template]
    else:
        return [run_template.format(src=src_path, out=out_path, dir=os.path.dirname(src_path), name=name)]

def run_program(cmd: list[str], input_data: str = "", timeout: float = 5.0) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, input=input_data, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise TimeoutError("Process timed out")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Process failed with code {e.returncode}: {e.stderr or e.stdout}")