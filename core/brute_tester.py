import time
import random
import os
import subprocess
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
        self.cleanup()

    def stop(self):
        self._should_stop = True

    def run_program_with_details(self, cmd, input_data, test_num, program_name):
        """Запускает программу и возвращает (stdout, stderr, returncode, timed_out, crashed)"""
        try:
            result = subprocess.run(
                cmd, 
                input=input_data, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout
            )
            return result.stdout, result.stderr, result.returncode, False, (result.returncode != 0)
        except subprocess.TimeoutExpired:
            return "", f"Timeout after {self.timeout}s", -1, True, True
        except Exception as e:
            return "", str(e), -1, False, True

    def run_tests(self, num_tests: int, stop_on_fail: bool,
                  progress_callback: Callable[[int, int], None] = None) -> Tuple[List[str], List[str]]:
        failed_tests = []
        errors = []
        
        for i in range(num_tests):
            if self._should_stop:
                break
                
            # Генерация теста
            try:
                gen_result = subprocess.run(
                    self.generator_cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=self.timeout
                )
                if gen_result.returncode != 0:
                    errors.append(f"Test {i+1}: Generator crashed with code {gen_result.returncode}\nStderr: {gen_result.stderr}")
                    if stop_on_fail:
                        break
                    continue
                test_input = gen_result.stdout
            except subprocess.TimeoutExpired:
                errors.append(f"Test {i+1}: Generator timeout after {self.timeout}s")
                if stop_on_fail:
                    break
                continue
            except Exception as e:
                errors.append(f"Test {i+1}: Generator error - {e}")
                if stop_on_fail:
                    break
                continue

            # Запуск решения
            sol_out, sol_err, sol_code, sol_timeout, sol_crashed = self.run_program_with_details(
                self.solution_cmd, test_input, i+1, "Solution"
            )
            
            # Запуск брута
            brute_out, brute_err, brute_code, brute_timeout, brute_crashed = self.run_program_with_details(
                self.brute_cmd, test_input, i+1, "Brute"
            )

            # Проверка на ошибки
            if sol_crashed or brute_crashed:
                error_msg = f"Test {i+1}:\nInput:\n{test_input}\n"
                if sol_crashed:
                    error_msg += f"Solution crashed:\n"
                    if sol_timeout:
                        error_msg += f"  Timeout after {self.timeout}s\n"
                    else:
                        error_msg += f"  Exit code: {sol_code}\n  Stderr: {sol_err}\n"
                if brute_crashed:
                    error_msg += f"Brute crashed:\n"
                    if brute_timeout:
                        error_msg += f"  Timeout after {self.timeout}s\n"
                    else:
                        error_msg += f"  Exit code: {brute_code}\n  Stderr: {brute_err}\n"
                errors.append(error_msg)
                if stop_on_fail:
                    break
                continue

            # Сравнение результатов
            if not equal_up_to_whitespace(sol_out, brute_out):
                failed_tests.append(
                    f"Test {i+1}:\nInput:\n{test_input}\n"
                    f"Solution output:\n{sol_out}\n"
                    f"Brute output:\n{brute_out}\n"
                    f"---"
                )
                if stop_on_fail:
                    break

            if progress_callback:
                progress_callback(i + 1, num_tests)

        return failed_tests, errors
    
    def cleanup(self):
        import os
        
        for cmd in [self.solution_cmd, self.brute_cmd, self.generator_cmd]:
            if not cmd:
                continue
            exe = cmd[0]
            filename = os.path.basename(exe)
            if filename.startswith('msm_') or filename.startswith('tmp_'):
                try:
                    if os.path.exists(exe):
                        os.remove(exe)
                except OSError:
                    pass