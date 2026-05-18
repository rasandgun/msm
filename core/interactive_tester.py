import subprocess
import threading
import time
import queue
import random
import os
from typing import List, Tuple, Callable, Optional
from core.runner import compile_program


class InteractiveTester:
    def __init__(self, solution_path: str, interactor_path: str, timeout: float = 3.0):
        self.solution_cmd = compile_program(solution_path)
        self.interactor_cmd = compile_program(interactor_path)
        self.timeout = timeout
        self._should_stop = False
        self.log_queue = queue.Queue()

    def stop(self) -> None:
        self._should_stop = True

    def run_single_test(self, seed: int) -> Tuple[bool, str, str]:
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
            return False, f"Failed to start processes: {e}", str(e)

        stop_forwarding = threading.Event()
        t1 = t2 = None

        def forward(src, dst, tag):
            try:
                for line in iter(src.readline, ""):
                    self.log_queue.put((tag, line))
                    if stop_forwarding.is_set() or self._should_stop:
                        break
                    dst.write(line)
                    dst.flush()
            except (BrokenPipeError, OSError):
                pass
            finally:
                try:
                    dst.close()
                except:
                    pass

        try:
            t1 = threading.Thread(target=forward, args=(p_sol.stdout, p_int.stdin, "sol->int"))
            t2 = threading.Thread(target=forward, args=(p_int.stdout, p_sol.stdin, "int->sol"))
            t1.daemon = True
            t2.daemon = True
            t1.start()
            t2.start()

            state = self._wait_for_completion(p_sol, p_int)
        finally:
            stop_forwarding.set()
            if t1:
                t1.join(timeout=0.5)
            if t2:
                t2.join(timeout=0.5)

        self._terminate_alive(p_sol, p_int)

        sol_stderr = _read_stderr(p_sol)
        int_stderr = _read_stderr(p_int)

        output = self._build_output(seed, state, sol_stderr, int_stderr)
        ok = self._is_success(state)

        return ok, output, int_stderr if int_stderr else sol_stderr

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
                    errors.append(error)
                    if stop_on_fail:
                        break
            except Exception as e:
                msg = f"Test {i+1} (seed {seed}) exception: {e}"
                errors.append(msg)
                if stop_on_fail:
                    break
            if progress_callback:
                progress_callback(i + 1, num_tests)
        return failed, errors

    def cleanup(self) -> None:
        for cmd in (self.solution_cmd, self.interactor_cmd):
            if not cmd:
                continue
            exe = cmd[0]
            if os.path.basename(exe).startswith("msm_"):
                try:
                    os.remove(exe)
                except OSError:
                    pass

    def _wait_for_completion(self, p_sol, p_int) -> dict:
        start = time.time()
        sol_done = False
        int_done = False
        sol_ret = None
        int_ret = None
        stopped_by_user = False
        timed_out = False

        while time.time() - start < self.timeout:
            if self._should_stop:
                stopped_by_user = True
                break

            if not sol_done and p_sol.poll() is not None:
                sol_done = True
                sol_ret = p_sol.returncode
                try:
                    p_sol.stdin.close()
                except:
                    pass

            if not int_done and p_int.poll() is not None:
                int_done = True
                int_ret = p_int.returncode
                try:
                    p_int.stdin.close()
                except:
                    pass

            if sol_done and int_done:
                break

            time.sleep(0.05 if (sol_done or int_done) else 0.01)

        if not stopped_by_user and not sol_done and not int_done:
            timed_out = True

        hung = None
        if not sol_done:
            hung = "Solution"
        if not int_done:
            hung = "Both" if hung else "Interactor"

        return {
            "timed_out": timed_out,
            "stopped_by_user": stopped_by_user,
            "sol_done": sol_done,
            "int_done": int_done,
            "sol_ret": sol_ret,
            "int_ret": int_ret,
            "hung": hung
        }

    def _terminate_alive(self, p_sol, p_int) -> None:
        for proc in (p_sol, p_int):
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

    def _build_output(self, seed: int, state: dict, sol_stderr: str, int_stderr: str) -> str:
        out = f"Seed {seed}:\nCommunication log:\n"
        while not self.log_queue.empty():
            tag, line = self.log_queue.get()
            out += f"{tag} {line}"
        out += "\n"

        if not self._is_success(state):
            out += "FAILED: "
            if state["stopped_by_user"]:
                out += "stopped by user; "
            elif state["timed_out"]:
                out += f"timeout - {state['hung'] or 'unknown'} hung; "
            elif not state["sol_done"] and state["int_done"]:
                out += "interactor finished, solution left waiting; "
            elif state["sol_done"] and not state["int_done"]:
                out += "solution finished, interactor left waiting; "
            elif not state["sol_done"] and not state["int_done"]:
                out += "both processes terminated unexpectedly; "
            else:
                out += f"interactor exited with code {state['int_ret']}; "

            if int_stderr.strip():
                out += f"\nInteractor stderr:\n{int_stderr.strip()}"
            if sol_stderr.strip():
                out += f"\nSolution stderr:\n{sol_stderr.strip()}"
        else:
            out += "OK"
        return out

    def _is_success(self, state: dict) -> bool:
        return (
            not state["timed_out"]
            and not state["stopped_by_user"]
            and state["sol_done"]
            and state["int_done"]
            and state["int_ret"] == 0
        )


def _read_stderr(proc) -> str:
    try:
        if proc and proc.stderr:
            return proc.stderr.read()
    except:
        pass
    return ""