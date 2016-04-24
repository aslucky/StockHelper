# coding:utf8

import sys

from PyQt4 import QtGui, QtCore, uic
from Setting import SettingWindow


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = uic.loadUi('../resource/main.ui', self)
        self.setWindowTitle("Stock Helper")
        self.setWindowIcon(QtGui.QIcon('../resource/app.png'))
        self.ui.checkBox_useTDXdata.toggle()

    @QtCore.pyqtSlot()
    def doSetting(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, "通达信数据路径")
        self.ui.lineEdit_tdxDataPath.setText(u'通达信数据路径: ' + dirName)
        # will be use setting window later
        # print("doSetting clicked")
        # self.setting = SettingWindow()
        # self.setting.show()

    @QtCore.pyqtSlot()
    def doSelect(self):
        print("doSelect clicked")

    @QtCore.pyqtSlot()
    def doUseTDX(self):
        print("doUseTDX clicked")

    @QtCore.pyqtSlot()
    def doMacdCross(self):
        print("doMacdCross clicked")

    @QtCore.pyqtSlot()
    def doMacdDiverse(self):
        print("doMacdDiverse clicked")


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
