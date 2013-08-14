# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Thu Aug 15 00:25:03 2013
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(460, 300)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.file_inst_list_path = QtGui.QPushButton(self.centralwidget)
        self.file_inst_list_path.setGeometry(QtCore.QRect(10, 90, 75, 23))
        self.file_inst_list_path.setObjectName(_fromUtf8("file_inst_list_path"))
        self.ar_path_button = QtGui.QPushButton(self.centralwidget)
        self.ar_path_button.setGeometry(QtCore.QRect(10, 40, 75, 23))
        self.ar_path_button.setObjectName(_fromUtf8("ar_path_button"))
        self.infoLabel = QtGui.QLabel(self.centralwidget)
        self.infoLabel.setGeometry(QtCore.QRect(10, 0, 441, 16))
        self.infoLabel.setObjectName(_fromUtf8("infoLabel"))
        self.textarea = QtGui.QTextBrowser(self.centralwidget)
        self.textarea.setGeometry(QtCore.QRect(95, 20, 371, 241))
        self.textarea.setObjectName(_fromUtf8("textarea"))
        self.wdir_button = QtGui.QPushButton(self.centralwidget)
        self.wdir_button.setGeometry(QtCore.QRect(10, 130, 75, 23))
        self.wdir_button.setObjectName(_fromUtf8("wdir_button"))
        self.begin_button = QtGui.QPushButton(self.centralwidget)
        self.begin_button.setGeometry(QtCore.QRect(10, 210, 75, 23))
        self.begin_button.setObjectName(_fromUtf8("begin_button"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 460, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))
        MainWindow.setMenuBar(self.menubar)
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Chroot Deployment", None))
        self.file_inst_list_path.setText(_translate("MainWindow", "Package List", None))
        self.ar_path_button.setText(_translate("MainWindow", "Archive Path", None))
        self.infoLabel.setText(_translate("MainWindow", "Archive path is optional. Default Path: /rogentos/", None))
        self.wdir_button.setText(_translate("MainWindow", "Output", None))
        self.begin_button.setText(_translate("MainWindow", "Begin", None))
        self.menuAbout.setTitle(_translate("MainWindow", "About", None))

