# coding:utf8
import csv
import datetime
import json
import operator
import os
import sys

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QDate, Qt, QVariant
from PyQt4.QtGui import QMessageBox

from dataProvider import DataProvider
from mainRes import Ui_MainWindow
from src import threadWorker
from src.strategy import Strategy, strategy_macdCross, strategy_macdDiverse
from src.threadWorker import WorkerDayRiseList, workerTypeDayRise, workerTypePickup, WorkerPickup
from utils import cur_file_path, get_legal_trade_date


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
        self.strategy = Strategy(self.dataProvider)
        # 选出来的股票信息 = pickupHeader
        self.codePickup = [[]]
        # 股票代码列表
        self.codeList = []
        self.workerDayRiseList = WorkerDayRiseList(self.dataProvider)
        self.workerPickup = None
        self.comboBox_klineType.addItems([u'30分钟', u'60分钟', u'日线', u'周线', u'月线'])
        self.kelineType = ['30', '60', 'D', 'W', 'M']
        self.comboBox_klineType.setCurrentIndex(2)
        # 暂时先放目录里面保存后面使用数据库
        if not os.path.exists(self.appPath + '/datas'):
            os.mkdir(self.appPath + '/datas')
        if not os.path.exists(self.appPath + '/pickup'):
            os.mkdir(self.appPath + '/pickup')

        tabledata = [['', '', '', '', '', '', '', '', '', '']]
        # set the table model
        self.header = [u'序号', u'代码', u'名称', u'涨跌幅', u'现价', u'开盘价', u'最高价', u'最低价', u'昨日收盘价', u'成交量', u'换手率']
        tm = DayListTableModel(tabledata, self.header, self)
        self.tableView_dayList.setModel(tm)

        tabledataPickup = [['', '', '', '', '', '']]
        self.pickupHeader = [u'序号', u'代码', u'名称', u'涨跌幅', u'现价', u'换手率']
        self.pickupModel = DayListTableModel(tabledataPickup, self.pickupHeader, self)
        self.tableView_pickup.setModel(self.pickupModel)

        configPath = self.appPath + '/config.json'
        if os.path.isfile(configPath):
            with open(configPath, 'r') as f:
                self.configData = json.load(f)
        if 'useTdx' in self.configData and self.configData['useTdx'] is 1:
            self.checkBox_useTDXdata.toggle()
        if 'macdCross' in self.configData and self.configData['macdCross'] is 1:
            self.checkBox_macdCross.toggle()
        if 'macdDivergence' in self.configData and self.configData['macdDivergence'] is 1:
            self.checkBox_macdDivergence.toggle()
        if 'savePickup' in self.configData and self.configData['savePickup'] is 1:
            self.checkBox_savePickup.toggle()

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
                self.do_pickup_save()
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
        print('object do_select thread id: {}'.format(QtCore.QThread.currentThreadId()))
        threadWorker.workerStop = False
        self.save_gui_config()
        self.enable_ui(0)
        self.codePickup = []
        self.tabWidget.setCurrentIndex(1)
        self.tableView_pickup.clearSpans()

        self.tradeDate = self.dateEdit_pickup.dateTime().toPyDateTime()
        legalDate = get_legal_trade_date(self.tradeDate)
        self.tradeDate = datetime.datetime.strptime(legalDate, "%Y-%m-%d")
        self.dateEdit_pickup.setDate(QDate.fromString(legalDate, 'yyyy-MM-dd'))

        if len(self.codeList) is 0:
            # 没有代码列表信息，需要重新获取一份
            self.codeList = self.dataProvider.get_code_list()
        if len(self.codeList) is 0:
            QtGui.QMessageBox.Warning(self, "StockHelper", '股票代码列表为空', QtGui.QMessageBox.Ok)
            return
        self.lable_top.setText(u'股票总数:{0} 已处理: 0 已选出: 0'.format(len(self.codeList)))
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
        self.workerPickup = WorkerPickup(self.tradeDate, self.codeList, self.kelineType[self.comboBox_klineType.currentIndex()], self.dataProvider, strategyFilter, self.strategy)
        self.workerPickup.moveToThread(self.workerThread)
        self.connect(self.workerPickup, QtCore.SIGNAL('work_finished'), self.work_finished)
        self.connect(self.workerPickup, QtCore.SIGNAL('updatePickup'), self.do_update_pickup)
        self.connect(self.workerPickup, QtCore.SIGNAL('progressUpdate'), self.progressUpdate)
        # 这里很关键，这样才会不阻塞界面线程
        self.workerPickup.start.emit()

    @QtCore.pyqtSlot()
    def progressUpdate(self, step):
        self.progressBar.setValue(step)
        self.lable_top.setText(u'股票总数:{} 已处理: {} 已选出: {}'.format(len(self.codeList), step, len(self.codePickup)))

    @QtCore.pyqtSlot()
    def do_stop(self):
        self.enable_ui(1)
        threadWorker.workerStop = True

    @QtCore.pyqtSlot()
    def do_setting(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, u"通达信数据路径")
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
    def do_update_pickup(self, pickup_data):
        """
        更新选股界面
        :param pickup_data: [u'序号', u'代码', u'名称', u'涨跌幅', u'现价', u'换手率']
        :return: 
        """
        self.codePickup.append(pickup_data)
        self.lable_top.setText(u'选股数量：%d' % len(self.codePickup))
        # set the table model
        self.pickupModel = DayListTableModel(self.codePickup, self.pickupHeader, self)
        self.tableView_pickup.setModel(self.pickupModel)

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
        if self.checkBox_savePickup.isChecked():
            self.configData['savePickup'] = 1
        else:
            self.configData['savePickup'] = 0
        # write to config file
        with open('config.json', 'w') as f:
            json.dump(self.configData, f)

    @QtCore.pyqtSlot()
    def do_pickup_save(self):
        if self.checkBox_savePickup.isChecked() and self.codePickup:
            # save to YYYYMMDD_macdCross.scv
            df = self.dataProvider.makeDataFrame(self.codePickup, self.pickupHeader)
            df.to_csv(self.appPath + '/pickup/macdCross_' + self.tradeDate.strftime("%Y-%m-%d") + '.csv', encoding='utf8')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec_())
