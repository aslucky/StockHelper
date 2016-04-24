# coding:utf8
import os
import sys
import json

import time
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QDate

from src.strategy import strategy
from utils import cur_file_path
from dataProvider import data_provider


# Subclassing QObject and using moveToThread
class workerThread(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def running(self):
        count = 0
        while count < 5:
            time.sleep(1)
            print "Increasing"
            count += 1
        self.finished.emit()


# Using a QRunnable
# http://qt-project.org/doc/latest/qthreadpool.html
# Note that a QRunnable isn't a subclass of QObject and therefore does
# not provide signals and slots.
class Runnable(QtCore.QRunnable):
    def run(self):
        count = 0
        app = QtCore.QCoreApplication.instance()
        while count < 5:
            print "Increasing"
            time.sleep(1)
            count += 1
        app.quit()



class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = uic.loadUi('../resource/main.ui', self)
        self.setWindowTitle("Stock Helper")
        self.setWindowIcon(QtGui.QIcon('../resource/app.png'))
        self.configData = {}
        self.appPath = cur_file_path()
        self.ui.progressBar.hide()
        configPath = self.appPath + '/config.json'
        if os.path.isfile(configPath):
            with open(configPath, 'r') as f:
                self.configData = json.load(f)
                print type(self.configData)
                # self.configData = eval(json.load(f))
        if self.configData.has_key('useTdx') and self.configData['useTdx'] is 1:
            self.ui.checkBox_useTDXdata.toggle()
        if self.configData.has_key('macdCross') and self.configData['macdCross'] is 1:
            self.ui.checkBox_macdCross.toggle()
        if self.configData.has_key('macdDivergence') and self.configData['macdDivergence'] is 1:
            self.ui.checkBox_macdDivergence.toggle()

        self.ui.dateEdit_pickup.setDate(QDate.currentDate())
        # load config
        # appPath = QtCore.QCoreApplication.applicationDirPath()
        # self.appPath = os.path.split(os.path.realpath(__file__))[0]

        if self.configData.has_key('tdxDataPath'):
            self.ui.lineEdit_tdxDataPath.setText(u'通达信数据路径: ' + self.configData['tdxDataPath'])

        # init data provider
        self.dataProvider = data_provider(self.appPath)

        # init strategy
        self.strategy = strategy()

    @QtCore.pyqtSlot()
    def doSetting(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, "通达信数据路径")
        if not dirName:
            return
        self.ui.lineEdit_tdxDataPath.setText(u'通达信数据路径: ' + dirName)
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
    def doSelect(self):
        runnable = Runnable()
        QtCore.QThreadPool.globalInstance().start(runnable)
    
        return 
        self.saveGUIConfig()
        codeList = []
        if self.ui.checkBox_useTDXdata.isChecked():
            if not self.configData.has_key('tdxDataPath'):
                QtGui.QMessageBox.Warning(self, "StockHelper", '数据路径未设置', QtGui.QMessageBox.Ok)
                return
            codeList = self.dataProvider.getCodeList(self.configData['tdxDataPath'], 0)
        else:
            codeList = self.dataProvider.getCodeList()

        trade_date = self.ui.dateEdit_pickup.dateTime().toPyDateTime()

        self.objThread = QtCore.QThread()
        worker = workerThread()
        worker.moveToThread(self.objThread)
        worker.finished.connect(self.objThread.quit)
        self.objThread.started.connect(worker.running)
        self.objThread.finished.connect(self.workDone)
        self.objThread.start()

        return
        pickupCode = []
        # apply strategy
        for code in codeList:
            klines = self.dataProvider.get_data_by_count(code, trade_date, 35, 'D')
            if len(klines) < 35:
                # 股票交易天数不足
                continue
            if self.ui.checkBox_macdCross.isChecked() and self.strategy.macdCross(klines):
                pickupCode.append(code)
                self.ui.ptx_out.setPlainText(code)
        # save to YYYYMMDD_macdCross.scv
        if self.ui.checkBox_savePickup.isChecked():
            output = open(self.appPath + '/macdCross_' + trade_date.strftime("%Y-%m-%d") + '.txt', 'w')
            output.write(str(pickupCode))
            output.close()

    def saveGUIConfig(self):
        if self.ui.checkBox_useTDXdata.isChecked():
            self.configData['useTdx'] = 1
        else:
            self.configData['useTdx'] = 0
        if self.ui.checkBox_macdCross.isChecked():
            self.configData['macdCross'] = 1
        else:
            self.configData['macdCross'] = 0
        if self.ui.checkBox_macdDivergence.isChecked():
            self.configData['macdDivergence'] = 1
        else:
            self.configData['macdDivergence'] = 0
        # write to config file
        with open('config.json', 'w') as f:
            json.dump(self.configData, f)

    @QtCore.pyqtSlot()
    def workDone(self):
        self.ui.ptx_out.setPlainText(u"操作完毕。")

    @QtCore.pyqtSlot()
    def doUseTDX(self):
        print("doUseTDX clicked")
        if self.ui.checkBox_useTDXdata.isChecked():
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
