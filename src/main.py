import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from tools.gui.MainForm import MainForm

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('logo.png'))
    main = MainForm()
    main.show()
    sys.exit(app.exec())
