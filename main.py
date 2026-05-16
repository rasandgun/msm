import sys
from PyQt5.QtGui import QFont    
print("Starting import...")
try:
    from PyQt5.QtWidgets import QApplication
    print("PyQt5 imported")
except Exception as e:
    print("PyQt5 error:", e)
    sys.exit(1)

from gui.main_window import MainWindow
print("MainWindow imported")

def main():
    print("Entering main()")
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 15)) 
    app.setApplicationName("Stress Tester Pro")
    window = MainWindow()
    window.show()
    print("Window shown")
    app.exec_()

if __name__ == "__main__":
    main()