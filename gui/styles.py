from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def set_style(main_window, theme: str):
    app = QApplication.instance()
    if theme == "dark":
        app.setStyle("Fusion")
        dark_palette = create_dark_palette()
        app.setPalette(dark_palette)
        app.setStyleSheet(DARK_QSS)
    else:
        app.setStyle("Fusion")
        light_palette = create_light_palette()
        app.setPalette(light_palette)
        app.setStyleSheet(LIGHT_QSS)

def create_dark_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.WindowText, QColor(208, 208, 208))
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ToolTipText, QColor(208, 208, 208))
    palette.setColor(QPalette.Text, QColor(208, 208, 208))
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, QColor(208, 208, 208))
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(128, 128, 128))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 128, 128))
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(80, 80, 80))
    return palette

def create_light_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, Qt.black)
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(128, 128, 128))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 128, 128))
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, Qt.white)
    return palette

DARK_QSS = """
QMainWindow { background-color: #2d2d2d; }
QMenuBar { background-color: #2d2d2d; color: #d0d0d0; }
QMenuBar::item:selected { background-color: #3a3a3a; }
QMenu { background-color: #2d2d2d; color: #d0d0d0; border: 1px solid #555; }
QMenu::item:selected { background-color: #3a3a3a; }
QToolBar { background-color: #2d2d2d; border-bottom: 1px solid #555; }
QStatusBar { background-color: #2d2d2d; color: #d0d0d0; }
QGroupBox {
    font-weight: bold;
    border: 1px solid #555;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
    color: #d0d0d0;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLineEdit, QSpinBox, QComboBox {
    background-color: #3c3c3c;
    color: #d0d0d0;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 3px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    selection-background-color: #2a82da;
    color: #d0d0d0;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #444;
    border: 1px solid #555;
    width: 16px;
}
QPushButton {
    background-color: #444;
    color: #d0d0d0;
    border: 1px solid #666;
    border-radius: 4px;
    padding: 5px 15px;
    font-weight: bold;
}
QPushButton:hover { background-color: #555; }
QPushButton:pressed { background-color: #2a82da; }
QPushButton:disabled { background-color: #3a3a3a; color: #888; }

QTabWidget::pane { border: 1px solid #555; background-color: #2d2d2d; }
QTabBar::tab {
    background-color: #383838;
    color: #d0d0d0;
    border: 1px solid #555;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 15px;
    margin-right: 2px;
}
QTabBar::tab:selected { background-color: #2d2d2d; }
QTabBar::tab:hover { background-color: #444; }

QTextEdit {
    background-color: #1e1e1e;
    color: #d0d0d0;
    border: 1px solid #555;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 13px;
}
QProgressBar {
    border: 1px solid #555;
    border-radius: 4px;
    text-align: center;
    color: #d0d0d0;
    background-color: #3a3a3a;
}
QProgressBar::chunk {
    background-color: #2a82da;
    border-radius: 3px;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background-color: #2d2d2d;
    border: 1px solid #555;
    width: 12px;
}
QScrollBar::handle {
    background-color: #555;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::add-line, QScrollBar::sub-line { height: 0px; }
"""

LIGHT_QSS = """
QMainWindow { background-color: #f0f0f0; }
QGroupBox {
    font-weight: bold;
    border: 1px solid #aaa;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLineEdit, QSpinBox, QComboBox {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 3px;
}
QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #aaa;
    border-radius: 4px;
    padding: 5px 15px;
}
QPushButton:hover { background-color: #d0d0d0; }
QPushButton:pressed { background-color: #2a82da; color: white; }
QTextEdit {
    border: 1px solid #ccc;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 13px;
}
QProgressBar {
    border: 1px solid #aaa;
    border-radius: 4px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #2a82da;
    border-radius: 3px;
}
QTabWidget::pane { border: 1px solid #aaa; }
QTabBar::tab {
    background-color: #e0e0e0;
    border: 1px solid #aaa;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 15px;
    margin-right: 2px;
}
QTabBar::tab:selected { background-color: #f0f0f0; }
QTabBar::tab:hover { background-color: #d0d0d0; }
"""