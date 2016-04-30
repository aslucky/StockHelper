# coding:utf8
import os

import datetime
import tushare as ts
import pandas as pd

from src.utils import getLastTradeDate


class DataProvider:
    """
    对外提供数据
    dataPath：本地数据路径
    """

    def __init__(self, app_path):
        self.appPath = app_path
        self.errString = ''
        self.lastTradeDate = getLastTradeDate()

    def get_code_list(self, dataPath=None, dataType=None):

        """
        获取当天的股票代码列表
        :param tdxPath: not None 遍历目录获取代码， is None 使用tushare获取当前交易日的股票列表
        :param dataType: 数据类型， 0 通达信数据
        :return: [] 股票代码列表
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
                codeList.to_csv(self.appPath + '/' + self.lastTradeDate + '_Datas.csv', encoding='utf8')
                # codeList = ts.get_today_all()
                if codeList is None:
                    print 'None data fetched'
                    return []
                # save to file don't need fetch every time, too slow
                codeList.to_csv(self.appPath + '/' + self.lastTradeDate + '_Datas.csv', encoding='utf8')
            else:
                codeList = pd.read_csv(self.appPath + '/' + self.lastTradeDate + '_Datas.csv', encoding='utf8',
                                       index_col=0, dtype={'code': str})
            return codeList['code']

    def get_day_rise(self):
        if not os.path.isfile(self.appPath + '/' + self.lastTradeDate + '_Datas.csv'):
            codeList = ts.get_today_all()
            codeList.to_csv(self.appPath + '/' + self.lastTradeDate + '_Datas.csv', encoding='utf8')
        else:
            codeList = pd.read_csv(self.appPath + '/' + self.lastTradeDate + '_Datas.csv', encoding='utf8',dtype={'code': str})
        # print codeList.ix[:,1:10]
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
            while len(spy) < count:
                # 新股等实际交易天数少于指定数量的情况
                # if holidays > count:
                #     break
                holidays *= 2
                startDate = trade_date + datetime.timedelta(days=-(count + holidays))
                spy = ts.get_hist_data(stock_code, start=startDate.strftime("%Y-%m-%d"),
                                       end=trade_date.strftime("%Y-%m-%d"),
                                       ktype=kline_type)
        except (RuntimeError, TypeError, NameError, IOError, ValueError):
            return []
        return spy[:count].sort_index()


if __name__ == '__main__':
    dp = DataProvider()
    print dp.dataPath

    dp1 = DataProvider('e:\\ss')
    print dp1.dataPath
    print get_code_List(os.path.split(os.path.realpath(__file__))[0])
