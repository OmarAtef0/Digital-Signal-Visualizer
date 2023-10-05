import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
import sys

def window():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(1000,200,600,600)
    label = QLabel("Hello, PyQt!", win)
    label.move(165, 100)
    button = QPushButton("Click Me", win)
    button.move(150, 150)
    win.show()
    sys.exit(app.exec())

    
window()
