# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import tushare as ts
import pandas as pd





if __name__ == '__main__':

    ts.set_token('4694dc0224bbf7818c559b53a71437ab0a4c1680bef74c29a2e6d14f')
    pro = ts.pro_api()

    # print((pd.Timestamp('now') - pd.Timedelta(days=365)).strftime('%Y%m%d'))
    # print(type(pd.Timestamp('now') - pd.Timedelta(days=365)))


    # print()
    # 获取螺纹钢主力最近一年的日线数据
    df = ts.pro_bar(ts_code='RB.SHF', start_date=(pd.Timestamp('now') - pd.Timedelta(days=365)).strftime('%Y%m%d'),
                    end_date=pd.Timestamp('now').strftime('%Y%m%d'), asset='FT', freq='D')

    # 将日期格式转换为backtrader需要的格式
    # df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')


    # 重新设置索引为日期
    df.set_index('trade_date', inplace=True)

    # print(df.sort_values(by='trade_date', ascending=False))
    df = df.sort_values(by='trade_date', ascending=True)
    # 将数据按backtrader需要的顺序存储到CSV文件中
    df.to_csv('rb.csv', columns=['open', 'high', 'low', 'close', 'vol', 'amount'], header=True)

    # df = pro.trade_cal(exchange='', start_date='20180901', end_date='20181001',
    #                    fields='exchange,cal_date,is_open,pretrade_date', is_open='0')
    # df = pro.daily(trade_date='20200325')

    # 接口描述：https://www.tushare.pro/document/2?doc_id=135
    # df = pro.fut_basic(exchange='SHFE', fut_type='2', fields='ts_code,symbol,name,list_date,delist_date')
    # 接口描述：https://www.tushare.pro/document/2?doc_id=138
    # 'RB.SHF'：螺纹钢主力， 'RBL.SHF'螺纹钢连续
    # df = pro.fut_daily(ts_code='RBL.SHF', start_date='20180101', end_date='20181113',fields='ts_code,trade_date,open,high,low,close,settle,vol')
    # print(df)
    # df.to_csv('SHFE.csv', header=False)
    # df1= pro.fut_mapping(ts_code='RB.SHF')
    # df1.to_csv('df1.csv', header=False)
    # df2= pro.fut_mapping(ts_code='RBL.SHF')
    # df2.to_csv('df2.csv', header=False)
    # df1.compare(df2).to_csv('testCsvCompare.csv')