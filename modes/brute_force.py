import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import runner
import subprocess

infinite_test_num = 2 ** 31
def equal_up_to_whitespace(str1, str2):
    return ''.join(str1.split()) == ''.join(str2.split())

class BruteForceTester:
    def __init__(self, solution_path, brute_path, generator_path):
        self.solution_path = solution_path
        self.brute_path = brute_path
        self.generator_path = generator_path
        self.solution_command = runner.compile_program_return_command(solution_path)
        self.brute_command = runner.compile_program_return_command(brute_path)
        self.generator_command = runner.compile_program_return_command(generator_path)
        self.compiled_files = []
        
    def generate_test(self):
        try:
            result = runner.run_program(self.generator_command)
            return result.stdout
        except Exception as e:
            raise Exception(f'Failed to generate test: {str(e)}')
    
    def run_tests(self, stop_on_fail, num_tests, progress_callback=None):
        failed_tests = []
        exceptional_tests = []
        
        for i in range(num_tests):
            if progress_callback:
                progress_callback(i + 1, num_tests)
                
            try:
                test = self.generate_test()
            except Exception as e:
                exceptional_tests.append(f"Generation failed: {str(e)}")
                if stop_on_fail:
                    break
                continue
            
            try:
                solution_out = runner.run_program(self.solution_command, test)
            except Exception as e:
                exceptional_tests.append(f"Solution failed on test {i+1}: {str(e)}\nTest:\n{test}")
                if stop_on_fail:
                    break
                continue
            
            try:
                brute_out = runner.run_program(self.brute_command, test)  # Fixed: was self.solution_command
            except Exception as e:
                exceptional_tests.append(f"Brute force failed on test {i+1}: {str(e)}\nTest:\n{test}")
                if stop_on_fail:
                    break
                continue
            
            if not equal_up_to_whitespace(solution_out.stdout, brute_out.stdout):
                failed_tests.append(f"Test {i+1}:\n{test}\nSolution output:\n{solution_out.stdout}\nBrute output:\n{brute_out.stdout}")
                if stop_on_fail:
                    break
        exceptional_tests.sort()
        failed_tests.sort()
        return exceptional_tests, failed_tests
    
    def cleanup(self):
        for cmd in [self.solution_command, self.brute_command, self.generator_command]:
            if cmd and cmd[0].startswith('./msm_'):
                try:
                    os.remove(cmd[0][2:])
                except:
                    pass

