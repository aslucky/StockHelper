# StockHelper
主要功能用来做选股，选股策略评测，买卖操作训练。

个人的一个兴趣爱好项目，同时欢迎感兴趣的朋友一起完善。
基于PyQt开发。  
第一阶段功能定义(2016.04.24)：  
macd金叉选股  
macd底背离选股

支持通达信导出的数据，可以在设置里面设置导出数据的路径  
通达信-系统-数据导出-高级导出-添加品种-沪深A股-全选-确定-开始导出  
导出设置：前复权，分隔格式逗号(,)，日期格式YYYY-MM-DD，不生成导出头部  
  
生成exe的方式：在src路径下执行 pyinstaller MainWindow.py  
生成的文件在src/dist目录下面  
  
修改了tushare的一个地方get_stock_basics为了保持和其他函数返回列的一致性，这里注释掉了，后面的程序可以统一处理格式

    # df = df.set_index('code')
    return df
