import multiprocessing
import os
import sys
import threading
from glob import glob

import numpy as np
import pandas as pd
from loguru import logger
from multiprocess import Pool
from pandas import DataFrame
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QFileDialog, QWidget
from tqdm import tqdm

from .qt.MainForm import Ui_Form_DFR
from .utils import calc_md5


def collect_file_info(file_list):
    df = pd.DataFrame(columns=['file_path', 'file_size', 'create_date', 'modify_date'])

    for file_path in file_list:

        file_size = os.path.getsize(file_path)

        if os.path.isdir(file_path) or file_size == 0:
            continue

        create_date = os.path.getctime(file_path)
        modify_date = os.path.getmtime(file_path)

        df = df.append({
            'file_path': file_path,
            'file_size': file_size,
            'create_date': create_date,
            'modify_date': modify_date
        },
                       ignore_index=True)

    return df


class WorkerThread(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path
        self.thread_flag = True

    def run(self):

        self.thread_flag = True

        logger.info(f'worker start... ')
        logger.info(f'parse {self.path}')

        # collect file list
        df = pd.DataFrame(columns=['file_path', 'file_size', 'create_date', 'modify_date'])
        file_list = glob(self.path + '/**', recursive=True)
        if (len(file_list) == 0):
            raise FileNotFoundError(f'Cannot find file: {self.path}')

        logger.info(f'parse {len(file_list)} files')

        if self.thread_flag == False:
            logger.info('worker stop!')
            return

        # parse file list
        if len(file_list) <= 32:
            workers = 1
        else:
            NUM_USABLE_CPU = max(multiprocessing.cpu_count() - 2, 1)
            workers = min(NUM_USABLE_CPU, len(file_list))

        file_list_temp = np.array_split(file_list, workers)

        with Pool(processes=workers) as p:
            results = list(tqdm(p.imap(lambda x: collect_file_info(x), file_list_temp), total=len(file_list_temp)))

        files_df = pd.concat(results)
        total_files_count = len(files_df)
        logger.info(f'parse {total_files_count} files finished.')

        if self.thread_flag == False:
            logger.info('worker stop!')
            return

        # find duplicate files by file_size and md5
        temp_df = files_df.groupby('file_size')
        source_file_size_count = len(temp_df)
        if (source_file_size_count == 0):
            logger.info('no duplicate file (file size) exists')
            return

        duplicate_file_size_df = pd.concat(g for _, g in temp_df if len(g) > 1)

        duplicate_file_size_count = len(duplicate_file_size_df)
        if self.thread_flag == False:
            logger.info('worker stop!')
            return

        duplicate_file_size_df['md5'] = duplicate_file_size_df['file_path'].apply(lambda x: calc_md5(x))
        temp_df = duplicate_file_size_df.groupby('md5')
        source_md5_count = len(temp_df)
        if (source_md5_count == 0):
            logger.info('no duplicate file (md5) exists')
            return

        duplicate_md5_df = pd.concat(g for _, g in temp_df if len(g) > 1)
        duplicate_md5_df.sort_values(by=['create_date', 'modify_date'], ascending=True, inplace=True)
        logger.info(duplicate_md5_df)

        duplicate_md5_count = len(duplicate_md5_df)

        if self.thread_flag == False:
            logger.info('worker stop!')
            return

        duplicate_md5_df['duplicate'] = duplicate_md5_df.duplicated(["md5"], keep="first")
        logger.info(duplicate_md5_df)

        removal_files_df = duplicate_md5_df[duplicate_md5_df['duplicate'] == True]
        logger.info(removal_files_df)

        removal_files_count = len(removal_files_df)
        if self.thread_flag == False:
            logger.info('worker stop!')
            return

        removal_files_df['file_path'].apply(lambda file: os.remove(file))

        logger.info(f'Duplicate File Removal finished!\n'
                    f'Total File: {total_files_count}\n'
                    f'Duplicate Files(File Size): {source_file_size_count} - {duplicate_file_size_count}\n'
                    f'Duplicate Files(MD5): {source_md5_count} - {duplicate_md5_count}\n'
                    f'Removal Files Count: {removal_files_count}')

    def stop(self):
        self.thread_flag = False


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
        logger.add(self.stream)

        self.gui.textEdit_Log.document().setMaximumBlockCount(4096)

        # Button
        self.gui.pushButton_Open.clicked.connect(self.open)
        self.gui.pushButton_Start.clicked.connect(self.start)

    def log(self, text):
        self.gui.textEdit_Log.moveCursor(QtGui.QTextCursor.End)
        self.gui.textEdit_Log.insertPlainText(text)
        self.gui.textEdit_Log.moveCursor(QtGui.QTextCursor.End)

    def open(self):
        self.path = QFileDialog.getExistingDirectory(self, 'Please Choose Source Direction', ".")
        self.gui.lineEdit_Path.setText(self.path)

    def start(self):
        if self.gui.pushButton_Start.text() == 'Start':
            self.worker = WorkerThread(self.path)
            self.worker.start()
            self.gui.pushButton_Start.setText('Stop')
        else:
            self.worker.stop()
            self.gui.pushButton_Start.setText('Start')
