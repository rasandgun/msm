import sys
import os
sys.path.append(os.path.dirname(__file__))
import runner
import threading

def equal_up_to_whitespace(a, b):
    return "".join(a.split()) == "".join(b.split())

class BruteForceTester:
    def __init__(self, solution_path, brute_path, generator_path, stop_event=None):
        self.solution_cmd = runner.compile_program_return_command(solution_path)
        self.brute_cmd = runner.compile_program_return_command(brute_path)
        self.generator_cmd = runner.compile_program_return_command(generator_path)
        self.stop_event = stop_event if stop_event else threading.Event()

    def generate_test(self):
        try:
            return runner.run_program(self.generator_cmd).stdout
        except Exception as e:
            raise Exception("Generator failed: " + str(e))

    def run_tests(self, stop_on_fail, num_tests, progress_callback=None):
        failed = []
        errors = []
        for i in range(num_tests):
            if self.stop_event.is_set():
                break
            if progress_callback:
                progress_callback(i + 1, num_tests)

            try:
                test = self.generate_test()
            except Exception as e:
                errors.append(str(e))
                if stop_on_fail:
                    break
                continue

            try:
                sol = runner.run_program(self.solution_cmd, test)
            except Exception as e:
                errors.append("Solution error on test " + str(i+1) + ":\n" + str(e) + "\nTest:\n" + test)
                if stop_on_fail:
                    break
                continue

            try:
                bru = runner.run_program(self.brute_cmd, test)
            except Exception as e:
                errors.append("Brute error on test " + str(i+1) + ":\n" + str(e) + "\nTest:\n" + test)
                if stop_on_fail:
                    break
                continue

            if not equal_up_to_whitespace(sol.stdout, bru.stdout):
                failed.append("Test " + str(i+1) + ":\n" + test + "\nSolution:\n" + sol.stdout + "\nBrute:\n" + bru.stdout)
                if stop_on_fail:
                    break
        return errors, failed

    def cleanup(self):
        for cmd in (self.solution_cmd, self.brute_cmd, self.generator_cmd):
            if cmd and cmd[0].startswith("./msm_"):
                try:
                    os.remove(cmd[0][2:])
                except:
                    pass