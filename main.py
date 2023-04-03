# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
        ("period_me_short", 12),
        ("period_me_long", 26),
        ("period_dif", 9),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        # dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
        # isoformat（）  返回格式如'YYYY-MM-DD'的字符串；
        #
        # print("-------------self.dataclose-------------")
        # print(self.dataclose)
        # print("-------------self.dataclose[0]-------------")
        # print( self.dataclose[0])
        # print("-------------len(self.dataclose)-------------")
        # print(len(self.dataclose))
        #
        # print("--------- 打印 self 策略本身的 lines ----------")
        # print(self.lines.getlinealiases())
        # print("--------- 打印 self.datas 第一个数据表格的 lines ----------")
        # print(self.datas[0].lines.getlinealiases())

        # print('-----the size of the list is :-----')
        # print(len(self.dataclose))
        # print('-----the list is :-----')
        # print(*self.dataclose, sep = ",")
        # print('[-1], %.2f' % self.dataclose[-1])

    def __init__(self):
        # self.count = 0  # 用于计算 next 的循环次数
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close  # 可以简写成self.data.close,写全是self.data.lines.close
        self.dataopen = self.datas[0].open


        # 默认情况下，backtrader指向的是self.datas中的第一个导入的数据集，所以该数据集的调用方法可以直接省略引号
        # ，写法最简洁，有3种等价形式： self.datas[0]/self.data0/self.data
        # 本程序中，应该只导入了一个数据集，所以默认self.datas[0]指的就是这个导入的单一的数据集
        # print('start --inint-- %')
        # print("line的总长度：", self.data0.buflen())
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a MovingAverageSimple indicator
        # 调用Indicators模块的函数计算指标时，默认是对self.datas
        # 数据对象中的第一张表格中的第一条line （默认第一条line是
        # closeline）计算相关指标。以计算5日均线为例，各种不同级别的简写方式都是默认基于收盘价
        # close 计算5日均线，所以返回的结果都是一致的：

        # self.sma = bt.indicators.SimpleMovingAverage(
        #     self.datas[0], period=self.params.maperiod)

        # Indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                     subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

        #如果把这些都放开，因为计算这些指标的时间不一样，所以指标有效的日期也会变化。
        #即使不改变self.sma里面的参数，因为有效日期是所有指标一起算的，回测的结果也会有变化。.

        #中国方法：计算macd指标
        self.ema_short = bt.indicators.ExponentialMovingAverage(self.datas[0].close, period=self.p.period_me_short)
        self.ema_long = bt.indicators.ExponentialMovingAverage(self.datas[0].close, period=self.p.period_me_long)
        self.dif = self.ema_short - self.ema_long
        self.dea = bt.indicators.ExponentialMovingAverage(self.dif, period=self.p.period_dif)
        self.macd = (self.dif - self.dea)*2

        #backtrader方法：计算macd指标
        # macdF = bt.indicators.MACD()
        # self.dif2 = macdF.macd
        # self.dea2 = macdF.signal
        # self.macd2 = bt.indicators.MACDHisto().histo*2

    def notify_order(self, order):

        # notify是在next函数中触发的
        # 在一次next中，对相同的订单也可能触发多个通知（相同状态或者不同状态）。
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            # 提交和接受委托单不做任何处理
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        # 订单完成，记录。
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm), doprint=True)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm), doprint=True)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            # 取消、金额不足、拒绝

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        # 每一次的买卖，都会调用此函数。
        # 可以在空仓->开仓，或者开仓->空仓的时候使用这个函数计算持仓情况、盈利
        # 可以分类自己的买卖依据，比如是价值回归还是均值回复等，见扫地曾教程
        # 问题：如果在已经有仓位的基础之上开仓呢？不会出发这个函数
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):

#dhfaskidfhkalsdjfa
#dfjaskldfjhsakdjhf

#fdaslfd
#fadsofasdf
        print("当前时点（今日）：", 'datetime.date(0)', self.data.lines.datetime.date(0), 'close', self.data.lines.close[0])
        # %d整数 %f浮点数 %s字符串 %x十六进制整数
        self.log('Open, %.2f' % self.dataopen[0], doprint=True)  # %.2f表示以小数点后两位的形式输出
        self.log('Close, %.2f' % self.dataclose[0], doprint=True)  # %.2f表示以小数点后两位的形式输出

        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # pisiton 持仓的意思

            # Not yet ... we MIGHT BUY if ...
            if self.dif[0] > 5 and self.macd[0] > 0 and self.macd[0] > self.macd[-1] and self.dataopen[0] < self.dataclose[0]:
            # if self.dataclose[0] > self.sma[0]:
                # current close less than previous close
                self.log('BUY CREATE, %.2f' % self.dataclose[0], doprint=True)

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:
            if self.macd[0] < -5 or self.dataclose[0]*0.95 > self.buyprice:
            #if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0], doprint=True)

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

        # if self.dataclose[0] < self.dataclose[-1]:
        #     # current close less than previous close
        #
        #     if self.dataclose[-1] < self.dataclose[-2]:
        #         # previous close less than the previous close
        #
        #         # BUY, BUY, BUY!!! (with all possible default parameters)
        #         self.log('BUY CREATE, %.2f' % self.dataclose[0])
        #         self.buy()
        # print(f"------------- next 的第{self.count + 1}次循环 --------------")

        # print("当前时点（今日）：", 'datetime[0]', self.data.lines.datetime[0], 'close', self.data.lines.close[0])
        # print("已处理的数据点：", len(self.data))
        # print("line的总长度：", self.data.buflen())
    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # strats = cerebro.optstrategy(
    #     TestStrategy,
    #     maperiod=range(10, 31))

    # strats = cerebro.optstrategy(
    #     TestStrategy,
    #     maperiod=range(10, 31))

    # print(os.path.basename('/root/runoob.txt'))  # 返回文件名
    # print(os.path.dirname('/root/runoob.txt'))  # 返回目录路径
    # print(os.path.split('/root/runoob.txt'))  # 分割文件名与路径
    # print(os.path.join('root', 'test', 'runoob.txt'))  # 将目录和文件名合成一个路径'

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'datas/orcl-1995-2014.txt')
    datapath = os.path.join(modpath, 'rb.csv')
    # datapath1 = os.path.join(modpath, './datas/orcl-1995-2014.txt')  #ok
    # datapath2 = os.path.join(modpath, '../datas/orcl-1995-2014.txt') #不是当前目录，不可以
    # datapath3 = os.path.join(modpath, 'datas\orcl-1995-2014.txt')  #ok
    # datapath4 = os.path.join(modpath, '.\datas\orcl-1995-2014.txt') #ok
    # datapath5 = os.path.join(modpath, '..\datas\orcl-1995-2014.txt') #不是当前目录，不可以
    '''
    os.path.join()函数：连接两个或更多的路径名组件
    1.如果各组件名首字母不包含’/’，则函数会自动加上
    2.如果有一个组件是一个绝对路径，则在它之前的所有组件均会被舍弃
    3.如果最后一个组件为空，则生成的路径以一个’/’分隔符结尾
    '''

    # Create a Data Feed
    # data = bt.feeds.YahooFinanceCSVData(
    #     dataname=datapath,
    #     # Do not pass values before this date
    #     fromdate=datetime.datetime(2000, 1, 1),
    #     # Do not pass values after this date
    #     todate=datetime.datetime(2000, 3, 31),
    #     reverse=False)

    data = bt.feeds.GenericCSVData(
        dataname='rb.csv',
        fromdate=datetime(2021, 4, 1),
        todate=datetime(2022, 2, 2),
        nullvalue=0.0,
        dtformat=('%Y%m%d'),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=6
    )
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()
    #生成的图表里两个变量的解释：broker cash（当前剩余的现金）、value（当前的总资产，包括现金和股票价值）