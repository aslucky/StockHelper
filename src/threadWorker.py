# coding:utf-8

from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignal, pyqtSlot

# 工作线程类型，用于统一处理返回信息时做判断
workerTypeDayRise = 1
workerTypePickup = 2


class WorkerDayRiseList(QtCore.QObject):
    """
    获取涨幅排行榜的工作线程
    """
    start = pyqtSignal()
    progressRange = pyqtSignal(int)
    progressStep = QtCore.pyqtSignal(int, name="changed")

    def __init__(self, data_provider, parent=None):
        super(WorkerDayRiseList, self).__init__(parent)
        self.start.connect(self.run)
        self.dataProvider = data_provider

    @pyqtSlot()
    def run(self):
        # print('object worker thread id: {}'.format(QtCore.QThread.currentThreadId()))
        code_list = self.dataProvider.get_day_rise()
        self.emit(QtCore.SIGNAL('work_finished'), workerTypeDayRise, code_list)


class WorkerPickup(QtCore.QObject):
    """
    选股操作的工作线程
    """
    start = pyqtSignal()
    progressRange = pyqtSignal(int)
    progressStep = QtCore.pyqtSignal(int, name="changed")

    def __init__(self, tradeDate, codeList, dataProvider, strategy, strategyType,parent=None):
        super(WorkerPickup, self).__init__(parent)
        self.start.connect(self.run)
        self.tradeDate = tradeDate
        self.codeList = codeList
        self.dataProvider = dataProvider
        self.strategy = strategy
        self.strategyType = strategyType

    @pyqtSlot()
    def run(self):
        # apply strategy
        step = 1
        for code in self.codeList:
            self.emit(QtCore.SIGNAL('progressStep'), step)
            step += 1
            # pandas在线程里面有问题，\pandas\core\format.py:2087: RuntimeWarning: invalid value encountered in greater  has_large_values = (abs_vals > 1e8).any()
            for st in self.strategyType:
                self.emit(QtCore.SIGNAL('strategy'), st, code)
            # klines = self.dataProvider.get_data_by_count(code, self.tradeDate, 50, 'D')
            # # print code + ' %d ' % len(klines)
            # if len(klines) < 35:
            #     # 股票交易天数不足
            #     continue
        self.emit(QtCore.SIGNAL('work_finished'), workerTypeDayRise, [])


if __name__ == '__main__':
    pass
