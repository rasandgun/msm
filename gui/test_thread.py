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
        try:
            if self.mode == "Brute Force":
                self.log.emit("Compiling programs...")
                self._tester = BruteForceTester(self.sol, self.brute, self.gen, self.timeout)
            else:
                self.log.emit("Compiling solution and interactor...")
                self._tester = InteractiveTester(self.sol, self.brute, self.timeout)

            self.log.emit(f"Running {self.num_tests} tests...")
            failed, errors = self._tester.run_tests(
                self.num_tests, self.stop_on_fail,
                progress_callback=lambda cur, total: self.progress.emit(cur, total)
            )

            self.log.emit("\n=== Results ===")
            self.log.emit(f"Failed: {len(failed)}, Errors: {len(errors)}")

            for f in failed:
                self.failed.emit(f)
            for e in errors:
                self.error.emit(e)

            if not failed and not errors:
                self.log.emit("All tests passed!")
                self.status_message.emit("All tests passed")
            else:
                self.status_message.emit("Testing finished with failures/errors")

        except Exception as e:
            self.error.emit(f"Fatal error: {str(e)}")
            self.log.emit(f"Fatal error: {str(e)}")
        finally:
            if self._tester:
                self._tester.cleanup()
            self.finished.emit()

    def stop(self):
        if self._tester:
            self._tester.stop()
        self.status_message.emit("Stopped by user")