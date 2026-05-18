from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def set_style(main_window, theme: str):
    app = QApplication.instance()
    app.setStyle("Fusion")
    if theme == "dark":
        app.setPalette(_dark_palette())
        app.setStyleSheet("")          # убираем любой предыдущий QSS
    else:
        app.setPalette(app.style().standardPalette())
        app.setStyleSheet("")

def _dark_palette() -> QPalette:
    p = QPalette()
    p.setColor(QPalette.Window, QColor(45, 45, 45))
    p.setColor(QPalette.WindowText, QColor(208, 208, 208))
    p.setColor(QPalette.Base, QColor(35, 35, 35))
    p.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    p.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    p.setColor(QPalette.ToolTipText, QColor(208, 208, 208))
    p.setColor(QPalette.Text, QColor(208, 208, 208))
    p.setColor(QPalette.Button, QColor(45, 45, 45))
    p.setColor(QPalette.ButtonText, QColor(208, 208, 208))
    p.setColor(QPalette.BrightText, Qt.red)
    p.setColor(QPalette.Link, QColor(42, 130, 218))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, Qt.black)
    p.setColor(QPalette.Disabled, QPalette.WindowText, QColor(128, 128, 128))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 128, 128))
    p.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(80, 80, 80))
    return p