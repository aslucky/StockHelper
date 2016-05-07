# coding:utf-8

from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignal, pyqtSlot

# 工作线程类型，用于统一处理返回信息时做判断
from src.strategy import strategy_macdCross, strategy_macdDiverse

workerTypeDayRise = 1
workerTypePickup = 2

workerStop = False


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

    def __init__(self, tradeDate, codeList, klineType, dataProvider, strategyFilter, strategy, parent=None):
        """
        :param tradeDate:  交易日期
        :param codeList:  代码列表
        :param klineType: K线周期，[u'30分钟', u'60分钟', u'日线', u'周线', u'月线']
        :param strategyFilter:  选股策略过滤器
        :param parent: 
        :return: 
        """
        super(WorkerPickup, self).__init__(parent)
        self.start.connect(self.run)
        self.tradeDate = tradeDate
        self.codeList = codeList
        self.klineType = klineType
        self.dataProvider = dataProvider
        self.strategyFilter = strategyFilter
        self.strategy = strategy
        self.pickup = []


    @pyqtSlot()
    def run(self):
        self.pickup = []
        # apply strategy
        step = 1
        bingo = False
        codes = self.codeList.ix[:, 0]
        for code in codes:
            if workerStop:
                break
            self.emit(QtCore.SIGNAL('progressUpdate'), step)
            step += 1
            bingo = False
            for st in self.strategyFilter:
                if st == strategy_macdCross:
                    if self.strategy.macdCross(code, self.tradeDate, self.klineType):
                        bingo = True
                    else:
                        continue
                elif st == strategy_macdDiverse:
                    if self.strategy.macdDivergence(code, self.tradeDate, self.klineType):
                        bingo = True
                    else:
                        continue
            if not bingo:
                continue
            print code
            self.pickup.append(code)
            rowData = self.codeList[self.codeList['code'] == code]
            try:
                # 不同来源编码不一致，这里需要处理一下 
                stockName = unicode(rowData['name'].tolist()[0], 'utf-8')
            except:
                stockName = rowData['name'].tolist()[0]
            if 'pe' in rowData:
                # 需要获取涨跌幅，收盘价，换手率信息
                rowData = self.strategy.dataProvider.get_last_trade_data(code)
            self.emit(QtCore.SIGNAL('updatePickup'), [len(self.pickup), code, stockName, '%.02f' % rowData['changepercent'], '%.02f' % rowData['trade'], '%.02f' % rowData['turnoverratio']])
        self.emit(QtCore.SIGNAL('work_finished'), workerTypePickup, [])


if __name__ == '__main__':
    pass
