import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modes'))
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading

from brute_force import BruteForceTester
from interactive import InteractiveTester



class TesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MSM GUI")
        root.tk.call('source', 'azure.tcl') 
        root.tk.call('set_theme', 'light') 
        self.root.geometry("800x800")

        self.tester = None
        self.running = False

        self.setup_ui()
        self.on_mode_change()

    def setup_ui(self):
        main = ttk.Frame(self.root, padding="10")
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        ttk.Label(main, text="Mode:").grid(row=0, column=0, sticky="w", pady=5)
        self.mode_var = tk.StringVar(value="Brute Force")
        mode_cb = ttk.Combobox(main, textvariable=self.mode_var,
                                values=["Brute Force", "Interactive"], state="readonly")
        mode_cb.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        mode_cb.bind("<<ComboboxSelected>>", self.on_mode_change)

        file_frame = ttk.LabelFrame(main, text="Files", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Solution:").grid(row=0, column=0, sticky="w", pady=(5, 10))
        self.sol_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.sol_var).grid(row=0, column=1, sticky="ew", padx=(5, 10))
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse(self.sol_var)).grid(row=0, column=2)

        self.brute_label = ttk.Label(file_frame, text="Brute Force:")
        self.brute_label.grid(row=1, column=0, sticky="w", pady=(5, 10))
        self.brute_var = tk.StringVar()
        self.brute_entry = ttk.Entry(file_frame, textvariable=self.brute_var)
        self.brute_entry.grid(row=1, column=1, sticky="ew", padx=(5, 10))
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse(self.brute_var)).grid(row=1, column=2)

        self.gen_label = ttk.Label(file_frame, text="Generator:")
        self.gen_label.grid(row=2, column=0, sticky="w", pady=(5, 10))
        self.gen_var = tk.StringVar()
        self.gen_entry = ttk.Entry(file_frame, textvariable=self.gen_var)
        self.gen_entry.grid(row=2, column=1, sticky="ew", padx=(5, 10))
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse(self.gen_var)).grid(row=2, column=2)

        param_frame = ttk.LabelFrame(main, text="Parameters", padding="10")
        param_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        param_frame.columnconfigure(1, weight=1)

        ttk.Label(param_frame, text="Tests count:").grid(row=0, column=0, sticky="w", pady=5)
        self.num_var = tk.StringVar(value="100")
        ttk.Entry(param_frame, textvariable=self.num_var).grid(row=0, column=1, sticky="w", padx=5)

        self.stop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(param_frame, text="Stop on first fail", variable=self.stop_var).grid(row=1, column=0, columnspan=2, sticky="w")

        self.progress = ttk.Progressbar(main, variable=tk.DoubleVar(), maximum=100)
        self.progress.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        self.run_btn = ttk.Button(btn_frame, text="Run", command=self.run_tests)
        self.run_btn.pack(side="left", padx=5)
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_tests, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_output).pack(side="left", padx=5)

        out_frame = ttk.LabelFrame(main, text="Results", padding="10")
        out_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=10)
        out_frame.columnconfigure(0, weight=1)
        out_frame.rowconfigure(0, weight=1)
        main.rowconfigure(5, weight=1)

        self.notebook = ttk.Notebook(out_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        console_tab = ttk.Frame(self.notebook)
        self.notebook.add(console_tab, text="Console")
        self.console = scrolledtext.ScrolledText(console_tab, wrap="word", height=8)
        self.console.pack(fill="both", expand=True)

        fail_tab = ttk.Frame(self.notebook)
        self.notebook.add(fail_tab, text="Fails")
        self.fail_text = scrolledtext.ScrolledText(fail_tab, wrap="word", height=15)
        self.fail_text.pack(fill="both", expand=True)

        err_tab = ttk.Frame(self.notebook)
        self.notebook.add(err_tab, text="Errors")
        self.err_text = scrolledtext.ScrolledText(err_tab, wrap="word", height=15)
        self.err_text.pack(fill="both", expand=True)

    def browse(self, var):
        f = filedialog.askopenfilename()
        if f:
            var.set(f)

    def on_mode_change(self, event=None):
        mode = self.mode_var.get()
        if mode == "Brute Force":
            self.brute_label.config(text="Brute Force:")
            self.gen_label.grid()
            self.gen_entry.grid()
            self.gen_label.grid(row=2, column=0)
            self.gen_entry.grid(row=2, column=1)
        else:
            self.brute_label.config(text="Interactor:")
            self.gen_label.grid_remove()
            self.gen_entry.grid_remove()

    def log(self, msg):
        self.root.after(0, lambda: self.console.insert("end", msg + "\n") or self.console.see("end"))

    def update_progress(self, cur, total):
        self.root.after(0, lambda: self.progress.config(value=(cur/total*100)))

    def add_fail(self, txt):
        self.root.after(0, lambda: self.fail_text.insert("end", txt + "\n"))

    def add_err(self, txt):
        self.root.after(0, lambda: self.err_text.insert("end", txt + "\n"))

    def clear_output(self):
        self.console.delete(1.0, "end")
        self.fail_text.delete(1.0, "end")
        self.err_text.delete(1.0, "end")
        self.progress.config(value=0)

    def run_tests(self):
        if self.running:
            return
        sol = self.sol_var.get()
        sec = self.brute_var.get()
        gen = self.gen_var.get()
        mode = self.mode_var.get()
        if mode == "Brute Force":
            if not (sol and sec and gen):
                messagebox.showerror("Error", "Choose all three files")
                return
        else:
            if not (sol and sec):
                messagebox.showerror("Error", "Choose solution and interactor")
                return
        try:
            n = int(self.num_var.get())
            if n <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid number")
            return

        self.clear_output()
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.running = True

        t = threading.Thread(target=self._run, args=(sol, sec, gen, n, mode))
        t.daemon = True
        t.start()

    def _run(self, sol, sec, gen, n, mode):
        try:
            self.log("Compiling...")
            if mode == "Brute Force":
                self.tester = BruteForceTester(sol, sec, gen)
            else:
                self.tester = InteractiveTester(sol, sec)
            self.log("OK, running tests...")
            errors, fails = self.tester.run_tests(self.stop_var.get(), n, self.update_progress)
            self.log("\nDone. Tests: " + str(n))
            self.log("Fails: " + str(len(fails)) + ", Errors: " + str(len(errors)))
            for f in fails:
                self.add_fail(f)
            for e in errors:
                self.add_err(e)
            if fails:
                self.notebook.select(1)
            elif errors:
                self.notebook.select(2)
        except Exception as e:
            self.log("ERROR: " + str(e))
            self.add_err(str(e))
            self.notebook.select(2)
        finally:
            self.root.after(0, lambda: self.run_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            self.running = False
            if self.tester:
                self.tester.cleanup()

    def stop_tests(self):
        if self.tester:
            self.tester.stop()
        self.log("Stopping...")

if __name__ == "__main__":
    root = tk.Tk()
    app = TesterGUI(root)
    root.mainloop()