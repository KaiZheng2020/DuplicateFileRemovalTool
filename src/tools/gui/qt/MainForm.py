# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainForm.ui'
##
## Created by: Qt User Interface Compiler version 6.2.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QHBoxLayout,
    QLayout, QLineEdit, QPushButton, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_Form_DFR(object):
    def setupUi(self, Form_DFR):
        if not Form_DFR.objectName():
            Form_DFR.setObjectName(u"Form_DFR")
        Form_DFR.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form_DFR.sizePolicy().hasHeightForWidth())
        Form_DFR.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(Form_DFR)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.lineEdit_Path = QLineEdit(Form_DFR)
        self.lineEdit_Path.setObjectName(u"lineEdit_Path")
        self.lineEdit_Path.setMinimumSize(QSize(0, 30))

        self.horizontalLayout.addWidget(self.lineEdit_Path)

        self.pushButton_Open = QPushButton(Form_DFR)
        self.pushButton_Open.setObjectName(u"pushButton_Open")
        self.pushButton_Open.setMinimumSize(QSize(87, 30))

        self.horizontalLayout.addWidget(self.pushButton_Open)

        self.pushButton_Start = QPushButton(Form_DFR)
        self.pushButton_Start.setObjectName(u"pushButton_Start")
        self.pushButton_Start.setMinimumSize(QSize(87, 30))

        self.horizontalLayout.addWidget(self.pushButton_Start)

        self.horizontalLayout.setStretch(0, 5)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.groupBox_Log = QGroupBox(Form_DFR)
        self.groupBox_Log.setObjectName(u"groupBox_Log")
        self.gridLayout = QGridLayout(self.groupBox_Log)
        self.gridLayout.setObjectName(u"gridLayout")
        self.textEdit_Log = QTextEdit(self.groupBox_Log)
        self.textEdit_Log.setObjectName(u"textEdit_Log")
        font = QFont()
        font.setPointSize(10)
        self.textEdit_Log.setFont(font)

        self.gridLayout.addWidget(self.textEdit_Log, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_Log)


        self.retranslateUi(Form_DFR)

        QMetaObject.connectSlotsByName(Form_DFR)
    # setupUi

    def retranslateUi(self, Form_DFR):
        Form_DFR.setWindowTitle(QCoreApplication.translate("Form_DFR", u"Duplicate File Removal Tool", None))
        self.pushButton_Open.setText(QCoreApplication.translate("Form_DFR", u"Open", None))
        self.pushButton_Start.setText(QCoreApplication.translate("Form_DFR", u"Start", None))
        self.groupBox_Log.setTitle(QCoreApplication.translate("Form_DFR", u"Log", None))
    # retranslateUi

