from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QCheckBox,
    QProgressBar, QTabWidget, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QStatusBar, QAction, QToolBar
)
from PyQt5.QtCore import Qt
from core.config_manager import load_config, save_config
from gui.test_thread import TestRunnerThread
from gui.styles import set_style

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.tester_thread = None
        self.init_ui()
        self.load_config_to_ui()

    def init_ui(self):
        self.setWindowTitle("Stress Tester Pro")
        self.setMinimumSize(900, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        file_group = QGroupBox("Program files")
        form = QFormLayout()
        self.solution_edit = QLineEdit()
        form.addRow("Solution:", self._with_browse(self.solution_edit))
        self.brute_edit = QLineEdit()
        form.addRow("Brute / Interactor:", self._with_browse(self.brute_edit))
        self.generator_edit = QLineEdit()
        self.gen_label = QLabel("Generator:")
        self.gen_row = self._with_browse(self.generator_edit)
        form.addRow(self.gen_label, self.gen_row)
        file_group.setLayout(form)
        main_layout.addWidget(file_group)

        param_group = QGroupBox("Test parameters")
        param_layout = QVBoxLayout()
        top_params = QHBoxLayout()
        top_params.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Brute Force", "Interactive"])
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        top_params.addWidget(self.mode_combo)
        top_params.addWidget(QLabel("Number of tests:"))
        self.num_spin = QSpinBox()
        self.num_spin.setRange(1, 100_000)
        self.num_spin.setValue(100)
        top_params.addWidget(self.num_spin)
        top_params.addWidget(QLabel("Timeout (s):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(2)
        top_params.addWidget(self.timeout_spin)
        param_layout.addLayout(top_params)
        self.stop_check = QCheckBox("Stop on first failure")
        self.stop_check.setChecked(True)
        param_layout.addWidget(self.stop_check)
        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)

        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        self.run_btn = QPushButton("Run tests")
        self.run_btn.clicked.connect(self.run_tests)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_tests)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_output)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.clear_btn)
        progress_layout.addLayout(btn_layout)
        main_layout.addLayout(progress_layout)

        self.tabs = QTabWidget()
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.failed_text = QTextEdit()
        self.failed_text.setReadOnly(True)
        self.errors_text = QTextEdit()
        self.errors_text.setReadOnly(True)
        self.tabs.addTab(self.console_text, "Console")
        self.tabs.addTab(self.failed_text, "Failed tests")
        self.tabs.addTab(self.errors_text, "Errors")
        main_layout.addWidget(self.tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        save_act = QAction("Save config", self)
        save_act.triggered.connect(self.save_config_from_ui)
        file_menu.addAction(save_act)
        load_act = QAction("Load config", self)
        load_act.triggered.connect(self.load_config_to_ui)
        file_menu.addAction(load_act)
        file_menu.addSeparator()
        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        view_menu = menubar.addMenu("View")
        light_act = QAction("Light theme", self)
        light_act.triggered.connect(lambda: self.change_theme("light"))
        dark_act = QAction("Dark theme", self)
        dark_act.triggered.connect(lambda: self.change_theme("dark"))
        view_menu.addAction(light_act)
        view_menu.addAction(dark_act)

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)
        toolbar.addAction(save_act)
        toolbar.addAction(load_act)

        set_style(self, self.config.get("theme", "light"))

    def _with_browse(self, edit: QLineEdit) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(edit)
        btn = QPushButton("Browse")
        btn.clicked.connect(lambda: self.browse_file(edit))
        h.addWidget(btn)
        return w

    def browse_file(self, edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(self, "Select program file")
        if path:
            edit.setText(path)

    def _on_mode_changed(self, mode: str):
        visible = (mode == "Brute Force")
        self.gen_label.setVisible(visible)
        self.gen_row.setVisible(visible)

    def save_config_from_ui(self):
        self.config.update({
            "solution": self.solution_edit.text(),
            "brute": self.brute_edit.text(),
            "generator": self.generator_edit.text(),
            "mode": self.mode_combo.currentText(),
            "num_tests": self.num_spin.value(),
            "timeout": self.timeout_spin.value(),
            "stop_on_fail": self.stop_check.isChecked(),
        })
        save_config(self.config)
        self.status_bar.showMessage("Configuration saved")

    def load_config_to_ui(self):
        cfg = load_config()
        self.solution_edit.setText(cfg.get("solution", ""))
        self.brute_edit.setText(cfg.get("brute", ""))
        self.generator_edit.setText(cfg.get("generator", ""))
        idx = self.mode_combo.findText(cfg.get("mode", "Brute Force"))
        if idx >= 0:
            self.mode_combo.setCurrentIndex(idx)
        self.num_spin.setValue(int(cfg.get("num_tests", 100)))
        self.timeout_spin.setValue(int(cfg.get("timeout", 2)))
        self.stop_check.setChecked(cfg.get("stop_on_fail", True))
        self.config = cfg
        self.status_bar.showMessage("Configuration loaded")

    def change_theme(self, theme: str):
        set_style(self, theme)
        self.config["theme"] = theme
        save_config(self.config)

    def run_tests(self):
        if self.tester_thread and self.tester_thread.isRunning():
            return

        sol = self.solution_edit.text().strip()
        brute = self.brute_edit.text().strip()
        gen = self.generator_edit.text().strip() if self.mode_combo.currentText() == "Brute Force" else ""
        mode = self.mode_combo.currentText()
        num = self.num_spin.value()
        timeout = self.timeout_spin.value()
        stop = self.stop_check.isChecked()

        if not sol or not brute:
            QMessageBox.critical(self, "Error", "Solution and Brute/Interactor paths are required.")
            return
        if mode == "Brute Force" and not gen:
            QMessageBox.critical(self, "Error", "Generator is required for Brute Force mode.")
            return

        self.clear_output()
        self.save_config_from_ui()

        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.tester_thread = TestRunnerThread(sol, brute, gen, mode, num, stop, timeout)
        self.tester_thread.log.connect(self._append_console)
        self.tester_thread.failed.connect(self._append_failed)
        self.tester_thread.error.connect(self._append_error)
        self.tester_thread.progress.connect(self._update_progress)
        self.tester_thread.finished.connect(self._on_tests_finished)
        self.tester_thread.status_message.connect(self.status_bar.showMessage)
        self.tester_thread.start()

    def stop_tests(self):
        if self.tester_thread:
            self.tester_thread.stop()
            self.status_bar.showMessage("Stopping...")

    def _on_tests_finished(self):
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _append_console(self, text: str):
        self.console_text.append(text)
        self.console_text.ensureCursorVisible()

    def _append_failed(self, text: str):
        self.failed_text.append(text)
        self.failed_text.ensureCursorVisible()

    def _append_error(self, text: str):
        self.errors_text.append(text)
        self.errors_text.ensureCursorVisible()

    def _update_progress(self, cur: int, total: int):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(cur)

    def clear_output(self):
        self.console_text.clear()
        self.failed_text.clear()
        self.errors_text.clear()
        self.progress_bar.reset()