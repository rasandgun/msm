import time
import random
import os
from typing import List, Tuple, Callable
from core.runner import compile_program, run_program

def equal_up_to_whitespace(a: str, b: str) -> bool:
    return "".join(a.split()) == "".join(b.split())

class BruteForceTester:
    def __init__(self, solution_path, brute_path, generator_path, timeout=2.0):
        self.solution_cmd = compile_program(solution_path)
        self.brute_cmd = compile_program(brute_path)
        self.generator_cmd = compile_program(generator_path)
        self.timeout = timeout
        self._should_stop = False
    
    def __del__(self):
        print("Destructor")
        self.cleanup()

    def stop(self):
        self._should_stop = True

    def run_tests(self, num_tests: int, stop_on_fail: bool,
                  progress_callback: Callable[[int, int], None] = None) -> Tuple[List[str], List[str]]:
        failed_tests = []
        errors = []

        for i in range(num_tests):
            if self._should_stop:
                break

            try:
                test = run_program(self.generator_cmd, timeout=self.timeout).stdout
            except Exception as e:
                errors.append(f"Generator error on test {i+1}: {e}")
                if stop_on_fail:
                    break
                continue

            try:
                sol_out = run_program(self.solution_cmd, test, timeout=self.timeout).stdout
            except Exception as e:
                errors.append(f"Solution error on test {i+1}: {e}\nTest:\n{test}")
                if stop_on_fail:
                    break
                continue

            try:
                brute_out = run_program(self.brute_cmd, test, timeout=self.timeout).stdout
            except Exception as e:
                errors.append(f"Brute error on test {i+1}: {e}\nTest:\n{test}")
                if stop_on_fail:
                    break
                continue

            if not equal_up_to_whitespace(sol_out, brute_out):
                failed_tests.append(
                    f"Test {i+1}:\nInput:\n{test}\nSolution:\n{sol_out}\nBrute:\n{brute_out}"
                )
                if stop_on_fail:
                    break

            if progress_callback:
                progress_callback(i + 1, num_tests)

        return failed_tests, errors
    
    def cleanup(self):
        """Удаляет скомпилированные временные файлы."""
        import os
        import glob
        
        for cmd in [self.solution_cmd, self.brute_cmd, self.generator_cmd]:
            if not cmd:
                continue
            exe = cmd[0]
            filename = os.path.basename(exe)
            if filename.startswith('msm_') or filename.startswith('tmp_'):
                try:
                    if os.path.exists(exe):
                        os.remove(exe)
                        print(f"  Removed: {exe}")
                    else:
                        print(f"  File not found: {exe}")
                except OSError as e:
                    print(f"  Failed to remove {exe}: {e}")
            else:
                print(f"  Skipping (not temp file): {filename}")