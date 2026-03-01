import subprocess
import threading
import time
import random
import os
from runner import compile_program_return_command

class InteractiveTester:
    def __init__(self, solution_path, interactor_path, stop_event=None):
        self.solution_path = solution_path
        self.interactor_path = interactor_path
        self.solution_cmd = None
        self.interactor_cmd = None
        self.temp_files = []
        self.stop_event = stop_event if stop_event else threading.Event()
        self.compile()

    def compile(self):
        try:
            self.solution_cmd = compile_program_return_command(self.solution_path)
        except Exception as e:
            raise Exception(f"Failed to compile solution: {e}")

        try:
            self.interactor_cmd = compile_program_return_command(self.interactor_path)
        except Exception as e:
            raise Exception(f"Failed to compile interactor: {e}")

    def run_single_test(self, seed, timeout=5):
        try:
            p_solution = subprocess.Popen(
                self.solution_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except Exception as e:
            return False, f"Failed to start solution: {e}"

        try:
            p_interactor = subprocess.Popen(
                self.interactor_cmd + [str(seed)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except Exception as e:
            p_solution.terminate()
            return False, f"Failed to start interactor: {e}"

        stop_event = threading.Event()
        solution_stderr = []
        interactor_stderr = []

        def read_stderr(stream, storage):
            for line in stream:
                storage.append(line)
            stream.close()

        t_sol_stderr = threading.Thread(target=read_stderr, args=(p_solution.stderr, solution_stderr))
        t_int_stderr = threading.Thread(target=read_stderr, args=(p_interactor.stderr, interactor_stderr))
        t_sol_stderr.daemon = True
        t_int_stderr.daemon = True
        t_sol_stderr.start()
        t_int_stderr.start()

        def forward(src, dst, name):
            try:
                for line in src:
                    if stop_event.is_set() or self.stop_event.is_set():
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

        t_sol_to_int = threading.Thread(target=forward, args=(p_solution.stdout, p_interactor.stdin, "sol2int"))
        t_int_to_sol = threading.Thread(target=forward, args=(p_interactor.stdout, p_solution.stdin, "int2sol"))
        t_sol_to_int.daemon = True
        t_int_to_sol.daemon = True
        t_sol_to_int.start()
        t_int_to_sol.start()

        start_time = time.time()
        solution_done = False
        interactor_done = False

        while time.time() - start_time < timeout:
            if self.stop_event.is_set():
                break
            if not solution_done and p_solution.poll() is not None:
                solution_done = True
                try:
                    p_solution.stdin.close()
                except:
                    pass
            if not interactor_done and p_interactor.poll() is not None:
                interactor_done = True
                try:
                    p_interactor.stdin.close()
                except:
                    pass
            if solution_done and interactor_done:
                break
            time.sleep(0.1)

        timed_out = False
        if p_solution.poll() is None:
            p_solution.terminate()
            timed_out = True
        if p_interactor.poll() is None:
            p_interactor.terminate()
            timed_out = True

        stop_event.set()
        t_sol_to_int.join(timeout=1)
        t_int_to_sol.join(timeout=1)
        t_sol_stderr.join(timeout=1)
        t_int_stderr.join(timeout=1)

        sol_ret = p_solution.returncode
        int_ret = p_interactor.returncode

        error_details = []
        if timed_out:
            error_details.append(f"Timeout ({timeout}s)")
        if sol_ret != 0:
            error_details.append(f"Solution exited with code {sol_ret}")
        if int_ret != 0:
            error_details.append(f"Interactor exited with code {int_ret}")

        sol_stderr_str = "".join(solution_stderr).strip()
        int_stderr_str = "".join(interactor_stderr).strip()
        if sol_stderr_str:
            error_details.append(f"Solution stderr: {sol_stderr_str}")
        if int_stderr_str:
            error_details.append(f"Interactor stderr: {int_stderr_str}")

        success = (int_ret == 0) and not timed_out
        info = f"Seed: {seed}\n" + "\n".join(error_details) if error_details else "OK"
        return success, info

    def run_tests(self, stop_on_fail, num_tests, progress_callback=None):
        exceptional_tests = []
        failed_tests = []

        for i in range(num_tests):
            if self.stop_event.is_set():
                break

            seed = random.getrandbits(64)

            try:
                success, info = self.run_single_test(seed)
                if not success:
                    failed_tests.append(info)
                    if stop_on_fail:
                        break
            except Exception as e:
                exceptional_tests.append(f"Test {i+1} (seed {seed}) exception: {str(e)}")
                if stop_on_fail:
                    break

            if progress_callback:
                progress_callback(i+1, num_tests)

        return exceptional_tests, failed_tests

    def cleanup(self):
        pass