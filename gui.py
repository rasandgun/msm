import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import threading
import queue
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'modes'))
from brute_force import *

class TesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MSM GUI")
        self.root.geometry("800x800")
        
        self.tester = None
        self.running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Testing Mode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="Brute Force")
        mode_combo = ttk.Combobox(main_frame, textvariable=self.mode_var, 
                                 values=["Brute Force"], state="readonly")
        mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        file_frame = ttk.LabelFrame(main_frame, text="Program Files", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Solution:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.solution_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.solution_var).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file(self.solution_var)).grid(row=0, column=2, padx=(5, 0))
        
        ttk.Label(file_frame, text="Brute Force:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.brute_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.brute_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file(self.brute_var)).grid(row=1, column=2, padx=(5, 0))
        
        ttk.Label(file_frame, text="Generator:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.generator_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.generator_var).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file(self.generator_var)).grid(row=2, column=2, padx=(5, 0))
        
        param_frame = ttk.LabelFrame(main_frame, text="Test Parameters", padding="10")
        param_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        param_frame.columnconfigure(1, weight=1)
        
        ttk.Label(param_frame, text="Number of tests:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_tests_var = tk.StringVar(value="100")
        ttk.Entry(param_frame, textvariable=self.num_tests_var).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        self.stop_on_fail_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(param_frame, text="Stop on first failure", variable=self.stop_on_fail_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.run_button = ttk.Button(button_frame, text="Run Tests", command=self.run_tests)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_tests, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Output", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        output_frame = ttk.LabelFrame(main_frame, text="Test Results", padding="10")
        output_frame.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(output_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        console_frame = ttk.Frame(self.notebook)
        self.notebook.add(console_frame, text="Console")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        self.console_text = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=15)
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        failed_frame = ttk.Frame(self.notebook)
        self.notebook.add(failed_frame, text="Failed Tests")
        failed_frame.columnconfigure(0, weight=1)
        failed_frame.rowconfigure(0, weight=1)
        
        self.failed_text = scrolledtext.ScrolledText(failed_frame, wrap=tk.WORD, height=15)
        self.failed_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        errors_frame = ttk.Frame(self.notebook)
        self.notebook.add(errors_frame, text="Errors")
        errors_frame.columnconfigure(0, weight=1)
        errors_frame.rowconfigure(0, weight=1)
        
        self.errors_text = scrolledtext.ScrolledText(errors_frame, wrap=tk.WORD, height=15)
        self.errors_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        main_frame.rowconfigure(5, weight=1)
    
    def log_console(self, message):
        """Потокобезопасный вывод в консоль"""
        self.root.after(0, self._safe_log_console, message)
    
    def _safe_log_console(self, message):
        self.console_text.insert(tk.END, f"{message}\n")
        self.console_text.see(tk.END)
    
    def update_progress(self, current, total):
        self.root.after(0, self._safe_update_progress, current, total)
    
    def _safe_update_progress(self, current, total):
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
    
    def update_buttons_state(self, run_state, stop_state):
        self.root.after(0, self._safe_update_buttons, run_state, stop_state)
    
    def _safe_update_buttons(self, run_state, stop_state):
        self.run_button.config(state=run_state)
        self.stop_button.config(state=stop_state)
    
    def add_failed_test(self, text):
        self.root.after(0, self._safe_add_failed, text)
    
    def _safe_add_failed(self, text):
        self.failed_text.insert(tk.END, text + "\n")
    
    def add_error(self, text):
        self.root.after(0, self._safe_add_error, text)
    
    def _safe_add_error(self, text):
        self.errors_text.insert(tk.END, text + "\n")
    
    def switch_to_tab(self, tab_name):
        self.root.after(0, self._safe_switch_tab, tab_name)
    
    def _safe_switch_tab(self, tab_name):
        tabs = {"console": 0, "failed": 1, "errors": 2}
        self.notebook.select(tabs[tab_name])

    def browse_file(self, var):
        filename = filedialog.askopenfilename(
            title="Select program file",
            filetypes=[("All files", "*.*"), ("C++ files", "*.cpp"), ("Python files", "*.py"), ("Java files", "*.java")]
        )
        if filename:
            var.set(filename)
    
    def run_tests(self):
        if self.running:
            return
            
        solution_path = self.solution_var.get()
        brute_path = self.brute_var.get()
        generator_path = self.generator_var.get()
        
        if not all([solution_path, brute_path, generator_path]):
            messagebox.showerror("Error", "Please select all three program files")
            return
        
        try:
            num_tests = int(self.num_tests_var.get())
            if num_tests <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number of tests")
            return
        
        self._safe_clear_output()
        
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.running = True
        
        thread = threading.Thread(
            target=self._run_tests_thread,
            args=(solution_path, brute_path, generator_path, num_tests)
        )
        thread.daemon = True
        thread.start()
    
    def _run_tests_thread(self, solution_path, brute_path, generator_path, num_tests):
        try:
            self.log_console("Initializing tester...")
            self.tester = BruteForceTester(solution_path, brute_path, generator_path)
            self.log_console("Compilation successful!")
            
            self.log_console(f"Running {num_tests} tests...")
            exceptional_tests, failed_tests = self.tester.run_tests(
                self.stop_on_fail_var.get(),
                num_tests,
                progress_callback=self.update_progress
            )
            
            self.log_console("\n=== Test Results ===")
            self.log_console(f"Tests run: {num_tests}")
            self.log_console(f"Failed tests: {len(failed_tests)}")
            self.log_console(f"Exceptions: {len(exceptional_tests)}")
            
            if failed_tests:
                self.log_console("\nFailed tests found!")
                for test in failed_tests:
                    self.add_failed_test(test)
                self.switch_to_tab("failed")
            
            if exceptional_tests:
                self.log_console("\nExceptions occurred!")
                for error in exceptional_tests:
                    self.add_error(error)
                self.switch_to_tab("errors")
            
            if not failed_tests and not exceptional_tests:
                self.log_console("\nAll tests passed! ✓")
            
        except Exception as e:
            self.log_console(f"Error: {str(e)}")
            self.add_error(str(e))
            self.switch_to_tab("errors")
        finally:
            self.update_buttons_state(tk.NORMAL, tk.DISABLED)
            self.running = False
            
            if self.tester:
                self.tester.cleanup()
    
    def stop_tests(self):
        self.running = False
        self.log_console("Stopping tests...")
    
    def clear_output(self):
        self._safe_clear_output()
    
    def _safe_clear_output(self):
        self.console_text.delete(1.0, tk.END)
        self.failed_text.delete(1.0, tk.END)
        self.errors_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.notebook.select(0)