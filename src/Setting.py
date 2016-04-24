# coding:utf8

import sys

from PyQt4 import QtGui, QtCore, uic


class SettingWindow(QtGui.QDialog):
    def __init__(self):
        super(SettingWindow, self).__init__()
        self.ui = uic.loadUi('../resource/setting.ui', self)
        self.setWindowTitle("Stock Helper")
        self.setWindowIcon(QtGui.QIcon('../resource/app.png'))

    @QtCore.pyqtSlot()
    def tdxDataBrowse(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, "通达信数据路径")
        self.ui.ptx_out.setPlainText(u'通达信数据路径: ' + dirName)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = SettingWindow()
    gui.show()
    sys.exit(app.exec_())
