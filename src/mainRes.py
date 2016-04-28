# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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
        MainWindow.resize(776, 552)
        font = QtGui.QFont()
        font.setPointSize(9)
        MainWindow.setFont(font)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setMargin(1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pb_setting = QtGui.QPushButton(self.centralwidget)
        self.pb_setting.setObjectName(_fromUtf8("pb_setting"))
        self.horizontalLayout.addWidget(self.pb_setting)
        self.pb_select = QtGui.QPushButton(self.centralwidget)
        self.pb_select.setObjectName(_fromUtf8("pb_select"))
        self.horizontalLayout.addWidget(self.pb_select)
        self.dateEdit_pickup = QtGui.QDateEdit(self.centralwidget)
        self.dateEdit_pickup.setDateTime(QtCore.QDateTime(QtCore.QDate(2016, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateEdit_pickup.setObjectName(_fromUtf8("dateEdit_pickup"))
        self.horizontalLayout.addWidget(self.dateEdit_pickup)
        self.checkBox_useTDXdata = QtGui.QCheckBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_useTDXdata.sizePolicy().hasHeightForWidth())
        self.checkBox_useTDXdata.setSizePolicy(sizePolicy)
        self.checkBox_useTDXdata.setObjectName(_fromUtf8("checkBox_useTDXdata"))
        self.horizontalLayout.addWidget(self.checkBox_useTDXdata)
        self.checkBox_macdCross = QtGui.QCheckBox(self.centralwidget)
        self.checkBox_macdCross.setObjectName(_fromUtf8("checkBox_macdCross"))
        self.horizontalLayout.addWidget(self.checkBox_macdCross)
        self.checkBox_macdDivergence = QtGui.QCheckBox(self.centralwidget)
        self.checkBox_macdDivergence.setObjectName(_fromUtf8("checkBox_macdDivergence"))
        self.horizontalLayout.addWidget(self.checkBox_macdDivergence)
        self.checkBox_savePickup = QtGui.QCheckBox(self.centralwidget)
        self.checkBox_savePickup.setObjectName(_fromUtf8("checkBox_savePickup"))
        self.horizontalLayout.addWidget(self.checkBox_savePickup)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lineEdit_tdxDataPath = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit_tdxDataPath.setObjectName(_fromUtf8("lineEdit_tdxDataPath"))
        self.verticalLayout.addWidget(self.lineEdit_tdxDataPath)
        self.ptx_out = QtGui.QPlainTextEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ptx_out.setFont(font)
        self.ptx_out.setObjectName(_fromUtf8("ptx_out"))
        self.verticalLayout.addWidget(self.ptx_out)
        self.progressBar = QtGui.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 776, 18))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.action_Setting = QtGui.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.action_Setting.setFont(font)
        self.action_Setting.setObjectName(_fromUtf8("action_Setting"))
        self.menuFile.addAction(self.action_Setting)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.pb_select, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.doSelect)
        QtCore.QObject.connect(self.action_Setting, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.doSetting)
        QtCore.QObject.connect(self.pb_setting, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.doSetting)
        QtCore.QObject.connect(self.checkBox_useTDXdata, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), MainWindow.doUseTDX)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.pb_setting.setText(_translate("MainWindow", "设置通达信数据路径", None))
        self.pb_select.setText(_translate("MainWindow", "选股", None))
        self.dateEdit_pickup.setDisplayFormat(_translate("MainWindow", "yyyy/MM/dd", None))
        self.checkBox_useTDXdata.setText(_translate("MainWindow", "使用通达信数据", None))
        self.checkBox_macdCross.setText(_translate("MainWindow", "MACD金叉", None))
        self.checkBox_macdDivergence.setText(_translate("MainWindow", "MACD底背离", None))
        self.checkBox_savePickup.setText(_translate("MainWindow", "保存选股结果", None))
        self.menuFile.setTitle(_translate("MainWindow", "文件", None))
        self.action_Setting.setText(_translate("MainWindow", "设置", None))

