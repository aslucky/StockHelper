# coding:utf8
import os

import datetime
import tushare as ts
import pandas as pd

from src.utils import get_legal_trade_date


class DataProvider:
    """
    对外提供数据
    dataPath：本地数据路径
    """

    def __init__(self, app_path):
        self.appPath = app_path
        self.errString = ''
        self.lastTradeDate = get_legal_trade_date()
    
    def get_last_trade_data(self, code):
        data = ts.get_hist_data(code, self.lastTradeDate)
        data.rename(columns={'p_change': 'changepercent','close':'trade','turnover':'turnoverratio'}, inplace=True)
        return data

    def get_code_list(self, dataPath=None, dataType=None):

        """
        获取当天的股票代码列表
        :param tdxPath: not None 遍历目录获取代码， is None 使用tushare获取当前交易日的股票列表
        :param dataType: 数据类型， 0 通达信数据
        :return: dataframe 股票代码列表
        code,代码
        name,名称
        industry,所属行业
        area,地区
        pe,市盈率
        outstanding,流通股本
        totals,总股本(万)
        totalAssets,总资产(万)
        liquidAssets,流动资产
        fixedAssets,固定资产
        reserved,公积金
        reservedPerShare,每股公积金
        eps,每股收益
        bvps,每股净资
        pb,市净率
        timeToMarket,上市日期
        """
        if dataPath is not None:
            if dataType is 0:
                # 使用通达信的数据
                codeList = []
                for root, dirs, files in os.walk(dataPath):
                    for fn in files:
                        codeList.append(fn[0:-4])
                return codeList
            else:
                self.errString = '不支持的数据类型dataType:%d' % dataType
                return []
        else:
            if not os.path.isfile(self.appPath + '/' + self.lastTradeDate + '_Datas.csv'):
                codeList = ts.get_stock_basics()
                if codeList is None:
                    print 'None data fetched'
                    return []
                # 格式和涨幅排行榜格式不一致，所以不保存
                # codeList.to_csv(self.appPath + '/' + self.lastTradeDate + '_Datas.csv', encoding='utf8')
            else:
                codeList = pd.read_csv(self.appPath + '/' + self.lastTradeDate + '_Datas.csv', encoding='utf8',
                                       index_col=0, dtype={'code': str})
            return codeList

    def get_day_rise(self):
        if not os.path.isfile(self.appPath + '/datas/' + self.lastTradeDate + '_Datas.csv'):
            try:
                codeList = ts.get_today_all()
            except Exception:
                return []
            codeList.to_csv(self.appPath + '/datas/' + self.lastTradeDate + '_Datas.csv', encoding='utf8')
        else:
            codeList = pd.read_csv(self.appPath + '/datas/' + self.lastTradeDate + '_Datas.csv', encoding='utf8',index_col=0,dtype={'code': str})
        return codeList

    def get_data_by_count(self, stock_code, trade_date, count, kline_type, dataPath=None, dataType=None):
        """
        获取到指定日期的count根k线数据，通达信目前只支持日线数据
        :param stock_code:
        :param trade_date: 指定日期的数据
        :param count:
        :param kline_type: 数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
        :param dataPath: 数据路径
        :param dataType: 数据类型， 0 通达信数据
        :return: dataframe 从小到大日期排序
        """
        # 获取count日内的k线数据
        holidays = (count / 5) * 3
        startDate = trade_date + datetime.timedelta(days=-(count + holidays))
        try:
            spy = ts.get_hist_data(stock_code, start=startDate.strftime("%Y-%m-%d"),
                                   end=trade_date.strftime("%Y-%m-%d"),
                                   ktype=kline_type)
            for i in range(4):
                if len(spy) < count:
                    holidays *= 2
                    startDate = trade_date + datetime.timedelta(days=-(count + holidays))
                    spy = ts.get_hist_data(stock_code, start=startDate.strftime("%Y-%m-%d"),
                                           end=trade_date.strftime("%Y-%m-%d"),
                                           ktype=kline_type)
                else:
                    break
        except (RuntimeError, TypeError, NameError, IOError, ValueError):
            return []
        return spy[:count].sort_index()


if __name__ == '__main__':
    dp = DataProvider()
    print dp.dataPath

    dp1 = DataProvider('e:\\ss')
    print dp1.dataPath
    print dp.get_code_list(os.path.split(os.path.realpath(__file__))[0])
