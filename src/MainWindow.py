# coding:utf8
import os
import random
import sys
import json
import time

import datetime
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QDate

from src.strategy import strategy
from utils import cur_file_path
from dataProvider import data_provider
from mainRes import Ui_MainWindow

macdcross = 1
macdDivergence = 2


# Subclassing QObject and using moveToThread
class workerThreadPickup(QtCore.QThread):
    def __init__(self, tradeDate, codeList, strategy, parent=None):
        self.tradeDate = tradeDate
        self.codeList = codeList
        self.strategy = strategy
        self.parent = parent
        super(workerThreadPickup, self).__init__(parent)

    def run(self):
        pickupCode = []
        # apply strategy
        step = 1
        filterMacdCross = self.parent.checkBox_macdCross.isChecked()
        for code in self.codeList:
            self.emit(QtCore.SIGNAL('progress'), step)
            step += 1
            klines = self.parent.dataProvider.get_data_by_count(code, self.tradeDate, 50, 'D')
            # print code + ' %d ' % len(klines)
            if len(klines) < 35:
                # 股票交易天数不足
                continue
            # pandas在线程里面有问题，\pandas\core\format.py:2087: RuntimeWarning: invalid value encountered in greater  has_large_values = (abs_vals > 1e8).any()
            if filterMacdCross:
                self.emit(QtCore.SIGNAL('strategy'), macdcross, code, klines)

        self.emit(QtCore.SIGNAL('select finished'))


class MainWindow(QtGui.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = uic.loadUi('../resource/main.ui', self)
        # self.setupUi(self)
        self.setWindowTitle("Stock Helper")
        self.setWindowIcon(QtGui.QIcon('../resource/app.png'))
        self.configData = {}
        self.tradeDate = datetime.date.today()
        self.appPath = cur_file_path()
        self.progressBar.hide()
        self.progressBar.setTextVisible(True)
        self.codePickup = []
        self.worker = None

        configPath = self.appPath + '/config.json'
        if os.path.isfile(configPath):
            with open(configPath, 'r') as f:
                self.configData = json.load(f)
        if 'useTdx' in self.configData and self.configData['useTdx'] is 1:
            self.checkBox_useTDXdata.toggle()
        if 'macdCross' in self.configData and self.configData['macdCross'] is 1:
            self.checkBox_macdCross.toggle()
        if self.configData.has_key('macdDivergence') and self.configData['macdDivergence'] is 1:
            self.checkBox_macdDivergence.toggle()

        self.dateEdit_pickup.setDate(QDate.currentDate())
        if 'tdxDataPath' in self.configData:
            self.lineEdit_tdxDataPath.setText(u'通达信数据路径: ' + self.configData['tdxDataPath'])

        # init data provider
        self.dataProvider = data_provider(self.appPath)

        # init strategy
        self.strategy = strategy()

    @QtCore.pyqtSlot()
    def doSetting(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, "通达信数据路径")
        if not dirName:
            return
        self.lineEdit_tdxDataPath.setText(u'通达信数据路径: ' + dirName)
        tdxPath = {'tdxDataPath': unicode(dirName, 'utf8', 'ignore').encode('utf8')}
        self.configData['tdxDataPath'] = tdxPath
        json_str = json.dumps(tdxPath)
        # write to config file
        with open('config.json', 'w') as f:
            json.dump(json_str, f)
            # will be use setting window later
            # print("doSetting clicked")
            # self.setting = SettingWindow()
            # self.setting.show()

    @QtCore.pyqtSlot()
    def doAbout(self):
        QtGui.QMessageBox.information(self, "StockHelper", 'Version:' + datetime.date.today().strftime("%Y-%m-%d") + '\nEmail: ascomtohom@126.com', QtGui.QMessageBox.Ok)
        
    @QtCore.pyqtSlot()
    def updateProgressBar(self, val):
        self.progressBar.setValue(val)

    @QtCore.pyqtSlot()
    def doStrategy(self, type, code, klines):
        if type == macdcross:
            if self.strategy.macdCross(klines):
                self.codePickup.append(code)
                self.ptx_out.appendPlainText(code)
        elif type == macdDivergence:
            if self.strategy.macdDivergence(klines):
                self.codePickup.append(code)
                self.ptx_out.appendPlainText(code)
        else:
            QtGui.QMessageBox.Warning(self, "StockHelper", '未知策略', QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def selectFinished(self):
        # save to YYYYMMDD_macdCross.scv
        if self.checkBox_savePickup.isChecked():
            output = open(self.appPath + '/macdCross_' + self.tradeDate.strftime("%Y-%m-%d") + '.txt', 'w')
            output.write(str(self.codePickup))
            output.close()
        QtGui.QMessageBox.Warning(self, "StockHelper", '操作完成', QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def doSelect(self):
        self.saveGUIConfig()
        self.codePickup = []
        codeList = []
        if self.checkBox_useTDXdata.isChecked():
            if 'tdxDataPath' not in self.configData:
                QtGui.QMessageBox.Warning(self, "StockHelper", '数据路径未设置', QtGui.QMessageBox.Ok)
                return
            codeList = self.dataProvider.getCodeList(self.configData['tdxDataPath'], 0)
        else:
            codeList = self.dataProvider.getCodeList()

        self.tradeDate = self.dateEdit_pickup.dateTime().toPyDateTime()
        self.progressBar.setRange(1, len(codeList))
        self.progressBar.show()

        self.worker = workerThreadPickup(self.tradeDate, codeList, self.strategy, self)
        self.worker.start()
        self.connect(self.worker, QtCore.SIGNAL('progress'), self.updateProgressBar)
        self.connect(self.worker, QtCore.SIGNAL('strategy'), self.doStrategy)
        self.connect(self.worker, QtCore.SIGNAL('select finished'), self.selectFinished)

    def saveGUIConfig(self):
        if self.checkBox_useTDXdata.isChecked():
            self.configData['useTdx'] = 1
        else:
            self.configData['useTdx'] = 0
        if self.checkBox_macdCross.isChecked():
            self.configData['macdCross'] = 1
        else:
            self.configData['macdCross'] = 0
        if self.checkBox_macdDivergence.isChecked():
            self.configData['macdDivergence'] = 1
        else:
            self.configData['macdDivergence'] = 0
        # write to config file
        with open('config.json', 'w') as f:
            json.dump(self.configData, f)

    @QtCore.pyqtSlot()
    def workDone(self):
        self.ptx_out.setPlainText(u"操作完毕。")

    @QtCore.pyqtSlot()
    def doUseTDX(self):
        print("doUseTDX clicked")
        if self.checkBox_useTDXdata.isChecked():
            self.configData['useTdx'] = 1
        else:
            self.configData['useTdx'] = 0
        # write to config file
        with open('config.json', 'w') as f:
            json.dump(self.configData, f)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
