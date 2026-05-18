import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Stress Tester Pro")
    app.setOrganizationName("CP-Tools")

    try:
        app.setFont(QFont("Segoe UI", 10))
    except:
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()