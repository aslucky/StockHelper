# coding:utf8
import pandas as pd
import talib as ta

strategy_macdCross = 1
strategy_macdDiverse = 2


class Strategy():
    """
    选股策略
    """

    def __init__(self):
        pass

    def macdCross(self, klines):
        """
        是否符合macd金叉
        :param klines: 股票数据
        :return: True 金叉， False 没有金叉
        """
        analysis = pd.DataFrame(index=klines.index)
        analysis['macd'], analysis['macdsignal'], analysis['macdhist'] = ta.MACD(klines['close'].values)
        analysis = analysis[pd.notnull(analysis['macd'])]
        '''
                    macd(diff)  macdsignal(dea)  macdhist(macd)
        date
        2015-11-23  0.37        0.23      0.14
        2015-11-24  0.42        0.27      0.15
        2015-11-25  0.51        0.32      0.19
        '''
        dataLength = len(analysis)
        if not analysis.empty and analysis.iloc[dataLength - 1, 0] > analysis.iloc[dataLength - 1, 1] and \
                        analysis.iloc[dataLength - 2, 0] < analysis.iloc[dataLength - 2, 1]:
            return True
        return False

    def macdDivergence(self, klines):
        pass


if __name__ == '__main__':
    pass
