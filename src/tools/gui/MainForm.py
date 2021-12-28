import ctypes
import inspect
import sys

from loguru import logger
from PySide6 import QtGui
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QFileDialog, QWidget

from ..core.duplicate_file_removal_tool import DuplicateFileRemoval
from .widgets.MainForm import Ui_Form_DFR


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        logger.info("Thread is already closed.")
    elif res == 1:
        logger.info("Thread is closed.")
    else:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        logger.info("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class Stream(QObject):
    _log = Signal(str)

    def write(self, text):
        self._log.emit(str(text))

    def flush(self):
        QApplication.processEvents()


class MainForm(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.gui = Ui_Form_DFR()
        self.gui.setupUi(self)

        # Log
        self.stream = Stream()
        self.stream._log.connect(self.log)

        sys.stdout = self.stream
        sys.stderr = self.stream

        logger.add(self.stream, format="{time:YYYY-MM-DD HH:mm:ss} - {message}", level="INFO")

        self.gui.textEdit_Log.document().setMaximumBlockCount(4096)

        # Button
        self.gui.pushButton_Open.clicked.connect(self.open)
        self.gui.pushButton_Start.clicked.connect(self.start)

        logger.info('This tool will find and remove Duplicate Files')
        logger.info('1. find duplicate files by file size')
        logger.info('2. find duplicate files by file md5 within 1st step results')
        logger.info('3. keep the first file by create_date and modify_date, and remove other duplicate files')
        logger.info('The duplicate files will be moved to the Trash or Recycle Bin')

    def log(self, text):
        if '\r' in text:
            text = text.replace('\r', '').rstrip()
            cursor = self.gui.textEdit_Log.textCursor()
            # cursor.movePosition(QtGui.QTextCursor.End)
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.insertBlock()
            self.gui.textEdit_Log.setTextCursor(cursor)

        self.gui.textEdit_Log.insertPlainText(text)
        self.gui.textEdit_Log.moveCursor(QtGui.QTextCursor.End)

    def open(self):
        self.path = QFileDialog.getExistingDirectory(self, 'Please Choose Source Dir', ".")
        self.gui.lineEdit_Path.setText(self.path)

    def start(self):

        if len(self.path) <= 0:
            logger.info('Please Choose Source Dir at first')
        else:
            if self.gui.pushButton_Start.text() == 'Start':
                self.worker = DuplicateFileRemoval(self.path)
                self.worker.start()
                self.gui.pushButton_Start.setText('Stop')
            else:
                stop_thread(self.worker)
                self.gui.pushButton_Start.setText('Start')
