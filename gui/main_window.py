import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QCheckBox,
    QProgressBar, QTabWidget, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QToolBar, QAction, QStatusBar, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QFont, QIcon, QTextCursor
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
        set_style(self, self.config.get("theme", "light"))
    
    def init_ui(self):
        self.setWindowTitle("Stress Tester Pro")
        self.setMinimumSize(900, 700)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Группа выбора файлов
        file_group = QGroupBox("Program Files")
        form = QFormLayout()
        self.solution_edit = QLineEdit()
        browse_sol = QPushButton("Browse")
        browse_sol.clicked.connect(lambda: self.browse_file(self.solution_edit))
        form.addRow("Solution:", self._hbox(self.solution_edit, browse_sol))

        self.brute_edit = QLineEdit()
        browse_brute = QPushButton("Browse")
        browse_brute.clicked.connect(lambda: self.browse_file(self.brute_edit))
        form.addRow("Brute/Interactor:", self._hbox(self.brute_edit, browse_brute))

        self.generator_edit = QLineEdit()
        browse_gen = QPushButton("Browse")
        browse_gen.clicked.connect(lambda: self.browse_file(self.generator_edit))
        self.generator_label = QLabel("Generator:")
        self.generator_container = self._hbox(self.generator_edit, browse_gen)
        form.addRow(self.generator_label, self.generator_container)
        file_group.setLayout(form)
        main_layout.addWidget(file_group)

        # Группа параметров
        param_group = QGroupBox("Test Parameters")
        param_layout = QVBoxLayout()
        top_params = QHBoxLayout()
        top_params.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Brute Force", "Interactive"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        top_params.addWidget(self.mode_combo)
        top_params.addWidget(QLabel("Number of tests:"))
        self.num_spin = QSpinBox()
        self.num_spin.setRange(1, 100000)
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

        # Прогресс и кнопки
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)

        self.run_btn = QPushButton("Run Tests")
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

        # Вкладки с результатами
        self.tabs = QTabWidget()
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.failed_text = QTextEdit()
        self.failed_text.setReadOnly(True)
        self.errors_text = QTextEdit()
        self.errors_text.setReadOnly(True)

        self.tabs.addTab(self.console_text, "Console")
        self.tabs.addTab(self.failed_text, "Failed Tests")
        self.tabs.addTab(self.errors_text, "Errors")
        main_layout.addWidget(self.tabs)

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Меню и тулбар
        self.create_menu_toolbar()

    def create_menu_toolbar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        save_action = QAction("Save Config", self)
        save_action.triggered.connect(self.save_config_from_ui)
        file_menu.addAction(save_action)
        load_action = QAction("Load Config", self)
        load_action.triggered.connect(self.load_config_to_ui)
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        light_theme = QAction("Light Theme", self)
        light_theme.triggered.connect(lambda: self.change_theme("light"))
        dark_theme = QAction("Dark Theme", self)
        dark_theme.triggered.connect(lambda: self.change_theme("dark"))
        view_menu.addAction(light_theme)
        view_menu.addAction(dark_theme)

        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addAction(save_action)
        toolbar.addAction(load_action)

    def browse_file(self, edit):
        fname, _ = QFileDialog.getOpenFileName(self, "Select program file")
        if fname:
            edit.setText(fname)

    def on_mode_changed(self, text):
        visible = (text == "Brute Force")
        self.generator_label.setVisible(visible)
        self.generator_container.setVisible(visible)
        
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
        self.num_spin.setValue(cfg.get("num_tests", 100))
        self.timeout_spin.setValue(int(cfg.get("timeout", 2.0)))
        self.stop_check.setChecked(cfg.get("stop_on_fail", True))
        self.config = cfg
        self.status_bar.showMessage("Configuration loaded")

    def change_theme(self, theme):
        set_style(self, theme)
        self.config["theme"] = theme
        save_config(self.config)

    def run_tests(self):
        if self.tester_thread and self.tester_thread.isRunning():
            return

        sol = self.solution_edit.text().strip()
        brute = self.brute_edit.text().strip()
        gen = self.generator_edit.text().strip()
        mode = self.mode_combo.currentText()
        num = self.num_spin.value()
        timeout = self.timeout_spin.value()
        stop = self.stop_check.isChecked()

        if not sol or not brute:
            QMessageBox.critical(self, "Error", "Solution and Brute/Interactor paths are required.")
            return
        if mode == "Brute Force" and not gen:
            QMessageBox.critical(self, "Error", "Generator required for Brute Force mode.")
            return

        self.clear_output()
        self.save_config_from_ui()

        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.tester_thread = TestRunnerThread(sol, brute, gen, mode, num, stop, timeout)
        self.tester_thread.log.connect(self.append_console)
        self.tester_thread.failed.connect(self.append_failed)
        self.tester_thread.error.connect(self.append_error)
        self.tester_thread.progress.connect(self.update_progress)
        self.tester_thread.finished.connect(self.on_tests_finished)
        self.tester_thread.status_message.connect(self.status_bar.showMessage)
        self.tester_thread.start()

    def stop_tests(self):
        if self.tester_thread:
            self.tester_thread.stop()
            self.status_bar.showMessage("Stopping...")

    def on_tests_finished(self):
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def append_console(self, text):
        self.console_text.append(text)
        self.console_text.moveCursor(QTextCursor.End)

    def append_failed(self, text):
        self.failed_text.append(text)
        self.failed_text.moveCursor(QTextCursor.End)

    def append_error(self, text):
        self.errors_text.append(text)
        self.errors_text.moveCursor(QTextCursor.End)

    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def clear_output(self):
        self.console_text.clear()
        self.failed_text.clear()
        self.errors_text.clear()
        self.progress_bar.reset()

    @staticmethod
    def _hbox(*widgets):
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            h.addWidget(widget)
        return w