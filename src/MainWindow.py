# coding:utf8
import datetime
import json
import operator
import os
import sys

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QDate, Qt, QVariant

from DataProvider import DataProvider
from mainRes import Ui_MainWindow
from src import threadWorker
from src.strategy import Strategy, strategy_macdCross, strategy_macdDiverse
from src.threadWorker import WorkerDayRiseList, workerTypeDayRise, workerTypePickup, WorkerPickup
from utils import cur_file_path


class DayListTableModel(QtCore.QAbstractTableModel):
    """
    每日的涨幅排行榜
    """

    def __init__(self, datain, headerdata, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == QtCore.DescendingOrder:
            self.arraydata.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.workerThread = QtCore.QThread()
        self.ui = uic.loadUi('../resource/main.ui', self)
        # self.setupUi(self)
        self.setWindowTitle("Stock Helper")
        self.setWindowIcon(QtGui.QIcon('../resource/app.png'))
        self.configData = {}
        self.tradeDate = datetime.date.today()
        self.appPath = cur_file_path()
        self.progressBar.hide()
        self.progressBar.setTextVisible(True)
        # init data provider
        self.dataProvider = DataProvider(self.appPath)
        # init strategy
        self.strategy = Strategy()
        # 选出来的股票信息 = pickupHeader
        self.codePickup = [[]]
        # 股票代码列表
        self.codeList = []
        self.workerDayRiseList = WorkerDayRiseList(self.dataProvider)
        self.workerPickup = None

        tabledata = [['', '', '', '', '', '', '', '', '', '']]
        # set the table model
        self.header = [u'序号', u'代码', u'名称', u'涨跌幅', u'现价', u'开盘价', u'最高价', u'最低价', u'昨日收盘价', u'成交量', u'换手率']
        tm = DayListTableModel(tabledata, self.header, self)
        self.tableView_dayList.setModel(tm)

        tabledataPickup = [['', '', '', '', '', '']]
        self.pickupHeader = [u'序号', u'代码', u'名称', u'涨跌幅', u'现价', u'换手率']
        tm = DayListTableModel(tabledataPickup, self.pickupHeader, self)
        self.tableView_pickup.setModel(tm)

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

        self.statusBar().showMessage(u"就绪...")

    def enable_ui(self, is_enable):
        if 0 == is_enable:
            self.pb_select.setEnabled(False)
            self.pb_dayRise.setEnabled(False)
            self.pb_setting.setEnabled(False)
        else:
            self.pb_select.setEnabled(True)
            self.pb_dayRise.setEnabled(True)
            self.pb_setting.setEnabled(True)

    @QtCore.pyqtSlot()
    def work_finished(self, worker_type, datas):
        """
        :param worker_type: 
        :param datas: DataFrame 
        :return: 
        """
        if workerTypeDayRise == worker_type:
            self.codeList = datas
            # set the table model
            tm = DayListTableModel(datas.values.tolist(), self.header, self)
            self.tableView_dayList.setModel(tm)
            for i in range(11):
                self.tableView_dayList.resizeColumnToContents(i)
        elif workerTypePickup == worker_type:
            if self.checkBox_savePickup.isChecked():
                print 'count:%d' % len(self.codePickup)
                output = open(self.appPath + '/select_macd' + self.tradeDate.strftime("%Y-%m-%d") + '.txt', 'w')
                output.write(str(self.codePickup))
                output.close()
        else:
            QtGui.QMessageBox.Warning(self, "StockHelper", '未知工作类型', QtGui.QMessageBox.Ok)
        self.progressBar.hide()
        self.statusBar().showMessage(u"就绪...")
        self.enable_ui(1)

    @QtCore.pyqtSlot()
    def do_day_rise(self):
        self.tabWidget.setCurrentIndex(0)
        # 禁止连续点击
        self.enable_ui(0)
        # 涨幅排行榜线程
        self.workerThread.start()
        self.workerDayRiseList.moveToThread(self.workerThread)
        # self.workerDayRiseList.work_finished.connect(self.work_finished)
        self.connect(self.workerDayRiseList, QtCore.SIGNAL('work_finished'), self.work_finished)
        self.workerDayRiseList.progressStep.connect(self.progressBar.setValue)
        # 这里很关键，这样才会不阻塞界面线程
        self.workerDayRiseList.start.emit()

        self.statusBar().showMessage(u"正在载入数据...")

    @QtCore.pyqtSlot()
    def do_select(self):
        threadWorker.workerStop = False
        self.save_gui_config()
        self.enable_ui(0)
        self.codePickup = []
        self.tabWidget.setCurrentIndex(1)
        self.tradeDate = self.dateEdit_pickup.dateTime().toPyDateTime()
        if len(self.codeList) is 0:
            # 没有代码列表信息，需要重新获取一份
            self.codeList = self.dataProvider.get_code_list()
        if len(self.codeList) is 0:
            QtGui.QMessageBox.Warning(self, "StockHelper", '股票代码列表为空', QtGui.QMessageBox.Ok)
            return
        self.statusBar().showMessage(u"正在执行选股操作...")
        self.progressBar.setRange(0, len(self.codeList))
        self.progressBar.show()

        # 涨幅排行榜线程
        strategyFilter = []
        if self.checkBox_macdCross.isChecked():
            strategyFilter.append(strategy_macdCross)
        if self.checkBox_macdDivergence.isChecked():
            strategyFilter.append(strategy_macdDiverse)

        self.workerThread.start()
        self.workerPickup = WorkerPickup(self.tradeDate, self.codeList['code'], self.dataProvider, self.strategy, strategyFilter)
        self.workerPickup.moveToThread(self.workerThread)
        self.connect(self.workerPickup, QtCore.SIGNAL('work_finished'), self.work_finished)
        self.connect(self.workerPickup, QtCore.SIGNAL('strategy'), self.do_strategy)
        self.connect(self.workerPickup, QtCore.SIGNAL('progressStep'), self.progressBar.setValue)
        # 这里很关键，这样才会不阻塞界面线程
        self.workerPickup.start.emit()

    @QtCore.pyqtSlot()
    def do_stop(self):
        self.enable_ui(1)
        threadWorker.workerStop = True

    @QtCore.pyqtSlot()
    def do_setting(self):
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
            # print("do_setting clicked")
            # self.setting = SettingWindow()
            # self.setting.show()

    @QtCore.pyqtSlot()
    def do_about(self):
        QtGui.QMessageBox.information(self, "StockHelper", 'Version:2016-04-30' + '\nEmail: ascomtohom@126.com',
                                      QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def do_strategy(self, strategy_type, code, klines):
        rowData = klines.ix[len(klines) - 1]
        bingo = False
        for st in strategy_type:
            if st == strategy_macdCross:
                if self.strategy.macdCross(klines):
                    bingo = True
                else:
                    return 
            elif st == strategy_macdDiverse:
                if self.strategy.macdDivergence(klines):
                    bingo = True
                else:
                    return
            else:
                QtGui.QMessageBox.Warning(self, "StockHelper", '未知策略', QtGui.QMessageBox.Ok)
        
        try:
            stockName = unicode(self.codeList[self.codeList['code'] == code]['name'].tolist()[0], 'utf-8')
        except:
            stockName = self.codeList[self.codeList['code'] == code]['name'].tolist()[0]
        self.codePickup.append(
            [len(self.codePickup) + 1, code, stockName, '%.02f' % rowData['p_change'], '%.02f' % rowData['close'],
             '%.02f' % rowData['turnover']])
        # set the table model
        tm = DayListTableModel(self.codePickup, self.pickupHeader, self)
        self.tableView_pickup.setModel(tm)

    @QtCore.pyqtSlot()
    def select_finished(self):
        # save to YYYYMMDD_macdCross.scv
        if self.checkBox_savePickup.isChecked():
            output = open(self.appPath + '/macdCross_' + self.tradeDate.strftime("%Y-%m-%d") + '.txt', 'w')
            for line in self.codePickup:
                output.write("%s\n" % str(line))
            output.close()
        QtGui.QMessageBox.Warning(self, "StockHelper", '操作完成', QtGui.QMessageBox.Ok)

    def save_gui_config(self):
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
    def do_use_tdx(self):
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
