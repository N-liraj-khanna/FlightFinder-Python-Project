import sys
from PyQt5.QtWidgets import *
from ui_widgets import Starting
from pyqt5_plugins.examplebuttonplugin import QtGui


class GuiManager:
    def __init__(self):
        self.app = QApplication(sys.argv)

        main_widget = QStackedWidget()
        main_widget.setWindowTitle("Flight Finder")
        main_widget.setWindowIcon(QtGui.QIcon("view/flight.png"))

        starting_window = Starting(main_widget)
        main_widget.addWidget(starting_window)
        main_widget.setGeometry(283, 56, 800, 650)
        main_widget.show()

        sys.exit(self.app.exec())
