import subprocess
import threading
import time
import random
import os
from runner import compile_program_return_command

class InteractiveTester:
    def __init__(self, solution_path, interactor_path):
        self.solution_cmd = compile_program_return_command(solution_path)
        self.interactor_cmd = compile_program_return_command(interactor_path)
        self.stop_flag = False

    def run_single_test(self, seed, timeout=5):
        sol = subprocess.Popen(self.solution_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, bufsize=1)
        inter = subprocess.Popen(self.interactor_cmd + [str(seed)], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        stop = threading.Event()
        sol_err, inter_err = [], []

        def read_err(pipe, store):
            for line in pipe:
                store.append(line)
            pipe.close()

        t1 = threading.Thread(target=read_err, args=(sol.stderr, sol_err))
        t2 = threading.Thread(target=read_err, args=(inter.stderr, inter_err))
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()

        def forward(src, dst, name):
            try:
                for line in src:
                    if stop.is_set():
                        break
                    dst.write(line)
                    dst.flush()
            except:
                pass
            finally:
                try:
                    dst.close()
                except:
                    pass

        t3 = threading.Thread(target=forward, args=(sol.stdout, inter.stdin, "sol2int"))
        t4 = threading.Thread(target=forward, args=(inter.stdout, sol.stdin, "int2sol"))
        t3.daemon = True
        t4.daemon = True
        t3.start()
        t4.start()

        start = time.time()
        sol_done = False
        inter_done = False

        while time.time() - start < timeout:
            if not sol_done and sol.poll() is not None:
                sol_done = True
                try:
                    sol.stdin.close()
                except:
                    pass
            if not inter_done and inter.poll() is not None:
                inter_done = True
                try:
                    inter.stdin.close()
                except:
                    pass
            if sol_done and inter_done:
                break
            time.sleep(0.05)

        timeout_flag = False
        if sol.poll() is None:
            sol.terminate()
            timeout_flag = True
        if inter.poll() is None:
            inter.terminate()
            timeout_flag = True

        stop.set()
        t3.join(1)
        t4.join(1)
        t1.join(1)
        t2.join(1)

        info = []
        if timeout_flag:
            info.append("Timeout")
        if sol.returncode != 0:
            info.append("Solution exit code " + str(sol.returncode))
        if inter.returncode != 0:
            info.append("Interactor exit code " + str(inter.returncode))
        if sol_err:
            info.append("Solution stderr: " + "".join(sol_err).strip())
        if inter_err:
            info.append("Interactor stderr: " + "".join(inter_err).strip())

        success = (inter.returncode == 0 and not timeout_flag)
        return success, "Seed: " + str(seed) + "\n" + "\n".join(info) if info else "OK"

    def run_tests(self, stop_on_fail, num_tests, progress_callback=None):
        errors = []
        fails = []
        for i in range(num_tests):
            if self.stop_flag:
                break
            seed = random.getrandbits(64)
            try:
                ok, msg = self.run_single_test(seed)
                if not ok:
                    fails.append(msg)
                    if stop_on_fail:
                        break
            except Exception as e:
                errors.append("Test " + str(i+1) + " seed " + str(seed) + ": " + str(e))
                if stop_on_fail:
                    break
            if progress_callback:
                progress_callback(i+1, num_tests)
        return errors, fails

    def stop(self):
        self.stop_flag = True

    def cleanup(self):
        pass