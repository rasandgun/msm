import os
import threading
from typing import List, Tuple, Callable
from core.runner import compile_program, run_program

def equal_up_to_whitespace(a: str, b: str) -> bool:
    return "".join(a.split()) == "".join(b.split())

class BruteForceTester:
    def __init__(self, solution_path: str, brute_path: str, generator_path: str, timeout: float = 2.0):
        self.solution_cmd = compile_program(solution_path)
        self.brute_cmd = compile_program(brute_path)
        self.generator_cmd = compile_program(generator_path)
        self.timeout = timeout
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run_tests(self, num_tests: int, stop_on_fail: bool,
                  progress_callback: Callable[[int, int], None] = None) -> Tuple[List[str], List[str]]:
        failed = []
        errors = []
        for i in range(num_tests):
            if self._stop_event.is_set():
                break

            try:
                test_input = run_program(self.generator_cmd, timeout=self.timeout).stdout
            except Exception as e:
                errors.append(f"Generator error on test {i+1}: {e}")
                if stop_on_fail:
                    break
                continue

            try:
                sol_out = run_program(self.solution_cmd, test_input, timeout=self.timeout).stdout
            except Exception as e:
                errors.append(f"Solution error on test {i+1}: {e}\nInput:\n{test_input}")
                if stop_on_fail:
                    break
                continue

            try:
                brute_out = run_program(self.brute_cmd, test_input, timeout=self.timeout).stdout
            except Exception as e:
                errors.append(f"Brute error on test {i+1}: {e}\nInput:\n{test_input}")
                if stop_on_fail:
                    break
                continue

            if not equal_up_to_whitespace(sol_out, brute_out):
                failed.append(
                    f"Test {i+1}:\nInput:\n{test_input}\n"
                    f"Solution:\n{sol_out}\nBrute:\n{brute_out}"
                )
                if stop_on_fail:
                    break

            if progress_callback:
                progress_callback(i + 1, num_tests)
        return failed, errors

    def cleanup(self) -> None:
        for cmd in (self.solution_cmd, self.brute_cmd, self.generator_cmd):
            exe = cmd[0]
            if os.path.basename(exe).startswith("msm_"):
                try:
                    os.remove(exe)
                except OSError:
                    pass