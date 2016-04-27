# coding:utf-8

import datetime
import os
import sys
import tushare as ts


def getLastTradeDate():
    last_trade_date = datetime.datetime.today()
    if int(last_trade_date.strftime("%w")) == 0:
        # sunday
        last_trade_date = last_trade_date + datetime.timedelta(days=-2)
    elif int(last_trade_date.strftime("%w")) == 6:
        # saturday
        last_trade_date = last_trade_date + datetime.timedelta(days=-1)
    return last_trade_date.strftime("%Y-%m-%d")


# 获取脚本文件的当前路径
def cur_file_path():
    # appPath = QtCore.QCoreApplication.applicationDirPath()
    # self.appPath = os.path.split(os.path.realpath(__file__))[0]
    # 获取脚本路径
    path = sys.path[0]
    # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，
    # 如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


def get_day_list():
    print "tushare version:" + ts.__version__
    '''
    获取当天的涨幅排行榜
    code
    name
    changepercent 涨跌幅
    trade:现价
    open:
    high:
    low:
    settlement:昨日收盘价
    volume:
    turnoverratio:
    '''
    all_data = ts.get_today_all()
    if all_data is None:
        print 'None data fetched'
        return

    trade_date = datetime.datetime.today()
    if int(trade_date.strftime("%w")) == 0:
        # sunday
        trade_date = trade_date + datetime.timedelta(days=-2)
    elif int(trade_date.strftime("%w")) == 6:
        # saturday
        trade_date = trade_date + datetime.timedelta(days=-1)

    all_data_file_name = "allData" + trade_date.strftime("%Y-%m-%d") + ".csv"
    output_all_data_file_dir = "e:/data/" + all_data_file_name
    all_data.to_csv(output_all_data_file_dir, encoding='gbk')
    # output_all_data_file_dir = "e:/data/" + all_data_file_name
    # up_data = pd.read_csv(output_all_data_file_dir, encoding='gbk', index_col=0, dtype={'code': str})
    print all_data['code']


if __name__ == '__main__':
    get_day_list()
