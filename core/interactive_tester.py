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
        
    def run_single_test(self, seed: int) -> Tuple[bool, str, str]:
        p_sol = None
        p_int = None
        t1 = t2 = None
        
        try:
            p_sol = subprocess.Popen(
                self.solution_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  
            )
            p_int = subprocess.Popen(
                self.interactor_cmd + [str(seed)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except Exception as e:
            return False, f"Failed to start processes: {e}", ""

        stop_forwarding = threading.Event()
        sol_output = []
        int_output = []
        
        def forward_with_log(src, dst, log, name):
            try:
                for line in iter(src.readline, ""):
                    if stop_forwarding.is_set() or self._should_stop:
                        break
                    log.append(f"[{name}] {line.rstrip()}")
                    dst.write(line)
                    dst.flush()
            except (BrokenPipeError, OSError):
                pass
            finally:
                try:
                    dst.close()
                except:
                    pass

        t1 = threading.Thread(target=forward_with_log, args=(p_sol.stdout, p_int.stdin, sol_output, "sol->int"))
        t2 = threading.Thread(target=forward_with_log, args=(p_int.stdout, p_sol.stdin, int_output, "int->sol"))
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()

        start = time.time()
        timed_out = False
        
        while time.time() - start < self.timeout:
            if self._should_stop:
                break
                
            if p_sol.poll() is not None and p_int.poll() is not None:
                break
                
            time.sleep(0.01)

        
        sol_stderr = ""
        int_stderr = ""
        
        if self._should_stop:
            timed_out = True
        
        
        for proc, name in [(p_sol, "Solution"), (p_int, "Interactor")]:
            if proc and proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=0.5)
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                if name == "Solution":
                    sol_stderr = proc.stderr.read() if proc.stderr else ""
                else:
                    int_stderr = proc.stderr.read() if proc.stderr else ""

        stop_forwarding.set()
        t1.join(timeout=0.5)
        t2.join(timeout=0.5)

        
        ok = (p_int.returncode == 0) and not timed_out and not self._should_stop

        output = f"Seed {seed}:\n"
        if sol_output:
            output += "Communication log:\n" + "\n".join(sol_output[-10:]) + "\n"
        if not ok:
            output += "FAILED: "
            if self._should_stop:
                output += "stopped by user; "
            if timed_out:
                output += "timeout; "
            if p_int.returncode != 0:
                output += f"interactor exit code {p_int.returncode}; "
            if int_stderr:
                output += f"\nInteractor stderr:\n{int_stderr}"
            if sol_stderr:
                output += f"\nSolution stderr:\n{sol_stderr}"
            return False, output, int_stderr
            
        output += "OK"
        return True, output, ""

    def run_tests(self, num_tests: int, stop_on_fail: bool,
                  progress_callback: Callable[[int, int], None] = None) -> Tuple[List[str], List[str]]:
        failed = []
        errors = []
        for i in range(num_tests):
            if self._should_stop:
                break
            seed = random.getrandbits(63)
            try:
                success, info, error = self.run_single_test(seed)
                if not success:
                    failed.append(info)
                    errors.append(error if error else info)
                    if stop_on_fail:
                        break
            except Exception as e:
                error_msg = f"Test {i+1} (seed {seed}) exception: {e}"
                errors.append(error_msg)
                if stop_on_fail:
                    break

            if progress_callback:
                progress_callback(i + 1, num_tests)

        return failed, errors

    def cleanup(self):
        import os
        for cmd in [self.solution_cmd, self.interactor_cmd]:
            if not cmd:
                continue
            exe = cmd[0]
            filename = os.path.basename(exe)
            if filename.startswith('msm_'):
                try:
                    if os.path.exists(exe):
                        os.remove(exe)
                except OSError:
                    pass