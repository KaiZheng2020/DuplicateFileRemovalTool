import sys
from multiprocessing import freeze_support

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QToolBar

from tools.gui.MainForm import MainForm

if __name__ == '__main__':

    freeze_support()

    app = QApplication(sys.argv)

    main = MainForm()
    main.show()
    sys.exit(app.exec())
