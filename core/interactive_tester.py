import subprocess
import threading
import time
import random
from typing import List, Tuple, Callable
from core.runner import compile_program

class InteractiveTester:
    def __init__(self, solution_path, interactor_path, timeout=3.0):
        self.solution_cmd = compile_program(solution_path)
        self.interactor_cmd = compile_program(interactor_path)
        self.timeout = timeout
        self._should_stop = False

    def stop(self):
        self._should_stop = True

    def run_single_test(self, seed: int) -> Tuple[bool, str]:
        try:
            p_sol = subprocess.Popen(
                self.solution_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            p_int = subprocess.Popen(
                self.interactor_cmd + [str(seed)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except Exception as e:
            return False, f"Failed to start processes: {e}"

        sol_stdout = []
        int_stdout = []
        stop_forwarding = threading.Event()

        def forward(src, dst, name):
            try:
                for line in iter(src.readline, ""):
                    if stop_forwarding.is_set() or self._should_stop:
                        break
                    dst.write(line)
                    dst.flush()
            except BrokenPipeError:
                pass
            finally:
                try:
                    dst.close()
                except:
                    pass

        t1 = threading.Thread(target=forward, args=(p_sol.stdout, p_int.stdin, "sol->int"))
        t2 = threading.Thread(target=forward, args=(p_int.stdout, p_sol.stdin, "int->sol"))
        t1.daemon = True; t2.daemon = True
        t1.start(); t2.start()

        start = time.time()
        while time.time() - start < self.timeout:
            if self._should_stop:
                break
            if p_sol.poll() is not None and p_int.poll() is not None:
                break
            time.sleep(0.05)

        timed_out = False
        if p_sol.poll() is None:
            p_sol.terminate(); timed_out = True
        if p_int.poll() is None:
            p_int.terminate(); timed_out = True

        stop_forwarding.set()
        t1.join(timeout=1); t2.join(timeout=1)

        sol_ret = p_sol.returncode
        int_ret = p_int.returncode
        ok = (int_ret == 0) and not timed_out

        if not ok:
            msg = f"Seed {seed}: "
            if timed_out:
                msg += "timeout; "
            if int_ret != 0:
                msg += f"interactor exit code {int_ret}; "
            return False, msg
        return True, f"Seed {seed}: OK"

    def run_tests(self, num_tests: int, stop_on_fail: bool,
                  progress_callback: Callable[[int, int], None] = None) -> Tuple[List[str], List[str]]:
        failed = []
        errors = []
        for i in range(num_tests):
            if self._should_stop:
                break
            seed = random.getrandbits(63)
            try:
                success, info = self.run_single_test(seed)
                if not success:
                    failed.append(info)
                    if stop_on_fail:
                        break
            except Exception as e:
                errors.append(f"Test {i+1} (seed {seed}) exception: {e}")
                if stop_on_fail:
                    break

            if progress_callback:
                progress_callback(i + 1, num_tests)

        return failed, errors

    def cleanup(self):
        pass