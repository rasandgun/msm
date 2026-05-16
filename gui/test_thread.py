from PyQt5.QtCore import QThread, pyqtSignal
from core.brute_tester import BruteForceTester
from core.interactive_tester import InteractiveTester

class TestRunnerThread(QThread):
    log = pyqtSignal(str)
    failed = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    status_message = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, sol, brute, gen, mode, num_tests, stop_on_fail, timeout):
        super().__init__()
        self.sol = sol
        self.brute = brute
        self.gen = gen
        self.mode = mode
        self.num_tests = num_tests
        self.stop_on_fail = stop_on_fail
        self.timeout = timeout
        self._tester = None

    def run(self):
        print("=== TestRunnerThread.run() START ===")
        self._tester = None
        try:
            print("  Creating tester...")
            if self.mode == "Brute Force":
                self.log.emit("Compiling programs...")
                self._tester = BruteForceTester(self.sol, self.brute, self.gen, self.timeout)
            else:
                self.log.emit("Compiling solution and interactor...")
                self._tester = InteractiveTester(self.sol, self.brute, self.timeout)
            
            print(f"  Tester created: {type(self._tester).__name__}")
            
            print("  Running tests...")
            failed, errors = self._tester.run_tests(
                self.num_tests, self.stop_on_fail,
                progress_callback=lambda cur, total: self.progress.emit(cur, total)
            )
            print("  Tests finished")
            
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            self.error.emit(f"Fatal error: {str(e)}")
            self.log.emit(f"Fatal error: {str(e)}")
        finally:
            print(f"  FINALLY block - _tester is {self._tester}")
            if self._tester:
                print(f"  Calling cleanup on {type(self._tester).__name__}")
                try:
                    self._tester.cleanup()
                    print("  Cleanup completed")
                except Exception as e:
                    print(f"  Cleanup ERROR: {e}")
            else:
                print("  WARNING: _tester is None, cleanup skipped!")
            self.finished.emit()
            print("=== TestRunnerThread.run() END ===")

    def stop(self):
        if self._tester:
            self._tester.stop()
        self.status_message.emit("Stopped by user")