# coding:utf8
import datetime
import pandas as pd
import talib as ta

strategy_macdCross = 1
strategy_macdDiverse = 2


class Strategy:
    """
    选股策略
    """

    def __init__(self, dataProvider):
        self.dataProvider = dataProvider

    def macdCross(self, code, date, klineType):
        """
        是否符合macd金叉
        :param klines: 股票数据
        :return: True 金叉， False 没有金叉
        """
        klines = self.dataProvider.get_data_by_count(code, date, 50, klineType)
        if len(klines) < 50:
            # 股票交易天数不足
            return
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
        if not analysis.empty and analysis.iloc[dataLength - 1, 0] > analysis.iloc[dataLength - 1, 1] and analysis.iloc[dataLength - 2, 0] < analysis.iloc[dataLength - 2, 1]:
            return True
        
        # analysis = analysis.sort_index(ascending=False)
        # # print analysis
        # '''
        #             macd(diff)  macdsignal(dea)  macdhist(macd)
        # date
        # 2015-11-25  0.51        0.32      0.19
        # 2015-11-24  0.42        0.27      0.15
        # 2015-11-23  0.37        0.23      0.14
        # '''
        # # macd diff上穿dea
        # if not analysis.empty and analysis.iloc[0, 0] > analysis.iloc[0, 1] and analysis.iloc[0 + 1, 0] < analysis.iloc[0 + 1, 1]:
        #     # print code + ' diff:%f '% analysis.iloc[0, 0] + 'dea:%f '%  analysis.iloc[0, 1] +' prediff:%f' % analysis.iloc[0 + 1, 0] + 'predea:%f '% analysis.iloc[0 + 1, 1]
        #     return True
        return False

    def get_low_price_macd(self, code, date, klineType):
        result = [code]
        # 取多少天的交易数据
        get_days = 50
        # 取50个交易日内的数据
        klines = self.dataProvider.get_data_by_count(code, date, get_days, klineType)
        # 新股交易天数不足
        if len(klines) != get_days:
            return []
        # 找到最低点的日期
        minDate = klines[klines['low'] == klines['low'].min()].index.tolist()
        # 日期
        result.append(minDate[0])
        # 最低价格
        result.append(klines['low'].min())
        # print minDate
        # 重新获取足够计算Macd的数据
        reklines = self.dataProvider.get_data_by_count(code, datetime.datetime.strptime(minDate[0], '%Y-%m-%d'), get_days, klineType)
        # 计算最低点的macd值
        analysis = pd.DataFrame(index=reklines.index)
        analysis['macd-DIFF'], analysis['macdsignal-DEA'], analysis['macdhist'] = ta.MACD(reklines['close'].values)
        # print analysis
        # print type(analysis)
        # print analysis.ix[minDate[0]]
        minMacd = analysis.ix[minDate[0]]
        # macd柱数值
        result.append(minMacd.ix[2])
        return result

    def macdDivergence(self, code, date, klineType):
        """
       macd底背离， 股价出现阶段性低点，macd柱出现阶段性高点
       :param kline_type: 'D' day,
       :rtype: True if checked, False not checked
       """
        # price, macdhist
        low_result = self.get_low_price_macd(code, date, klineType)
        if not low_result:
            return []
        # 从最低价之前的30个交易日开始找第二个低点
        trade_date = datetime.datetime.strptime(low_result[1], '%Y-%m-%d')
        trade_date += datetime.timedelta(days=-30)
        pre_low_result = self.get_low_price_macd(code, trade_date, klineType)
        if not pre_low_result:
            return []
        # 检查是否macd背离
        try:
            if pre_low_result[2] > low_result[2] and pre_low_result[3] < low_result[3]:
                return True
            else:
                return False
        except (RuntimeError, TypeError, NameError, IOError, ValueError):
            return False


if __name__ == '__main__':
    pass
