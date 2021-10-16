#选股脚本：通过对比日与当日股价涨跌幅和成交量进行选股。可以选择的参数是T-N天的N天可以自己定义；对比日选择股价可以是涨超多少或者跌超多少；
# 对照日成交量和当日成交量的百分之多少相比较，可以选择百分比；当日股价下跌不超过多少可以设定。

import akshare as ak
from numpy import empty
import pandas as pd
import datetime as dt
from chinese_calendar import is_workday,is_holiday
import time

start = time.perf_counter()
end = time.perf_counter()
t = end - start

#操作日
action_date = dt.date.today()
#A股当日所有股票
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
#A股所有股票代码
stock_code_spot_df = stock_zh_a_spot_em_df['代码']

#导出当天的A股所有明细，以当天的日期命名EXCEL文件
def export_A_stocks(date):
    stock_zh_a_spot_em_df.to_excel(str(date)+'.xls',sheet_name='A-stocks')
export_A_stocks(action_date)

#对比日日期，tradeback_days即为当天往前第几个交易日。
def contrast_date(tradeback_days):
    n = 1
    for i in range(tradeback_days):
        contrast_date = action_date + dt.timedelta(days = -i-n)
        date_flag = True
        while date_flag:
            if is_workday(contrast_date) and contrast_date.weekday() != 5 and contrast_date.weekday() != 6:
                contrast_date = contrast_date
                date_flag = False
            else:
                contrast_date = contrast_date + dt.timedelta(days =-1)
                n += 1
    return contrast_date
        

#对比日股票中股价上涨或者下跌的股票代码dataframe文件。参数：1，回测的第几天；2、是大于某个比例或者小于某个比例；3、涨跌幅比例。
def contrast_price_stocks(tradeback_days,direction_up=True,price_rate=None):
    contrast_price_stocks = pd.DataFrame()
    contrast_price_stock_codelist = []
    for stock_code in stock_code_spot_df.iteritems():
        try:
            stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=str(stock_code[1]), period="daily", start_date=str(contrast_date(tradeback_days)), end_date=str(contrast_date(tradeback_days)), adjust="qfq")
            if stock_zh_a_hist_df.empty == False:
                if direction_up:
                    if stock_zh_a_hist_df.iat[0,8]>price_rate:
                        contrast_price_stocks = contrast_price_stocks.append(stock_zh_a_hist_df,ignore_index=True)
                        contrast_price_stock_codelist.append(str(stock_code[1]))
                else:
                    if stock_zh_a_hist_df.iat[0,8]<price_rate:
                        contrast_price_stocks = contrast_price_stocks.append(stock_zh_a_hist_df,ignore_index=True)
                        contrast_price_stock_codelist.append(str(stock_code[1]))
        except ValueError:
            continue
    contrast_price_stocks.insert(0,'代码',contrast_price_stock_codelist)
    return contrast_price_stocks

#对比日股票成交量与当日成交量对比。
#选对比日成交量与当日成交量进行比较，参数是当日成交量的百分比，如果满足条件就挑出来。
def choosen_stocks(tradeback_days,direction_up,price_rate,turnover_rate,drop_rate):
    choosen_stocks = pd.DataFrame()
    contrast_stocks = contrast_price_stocks(tradeback_days,direction_up,price_rate)
    action_date_stocks = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['涨跌幅']<drop_rate]
    contrast_stocks_codes = contrast_stocks['代码']
    turnover_rate = turnover_rate
    for stock_code in contrast_stocks_codes.iteritems():
        #选取这一个代码所在行成交量，在对比日与当日成交量进行比较。
        try:
            contrast_turnover_stock = contrast_stocks[contrast_stocks['代码'].str.contains(stock_code[1])]
            action_date_turnover_stock = action_date_stocks[action_date_stocks['代码'].str.contains(stock_code[1])]
            if contrast_turnover_stock.iat[0,6] > turnover_rate * action_date_turnover_stock.iat[0,6]:
                choosen_stocks.append(action_date_turnover_stock)

        except IndexError:
            continue
    return choosen_stocks


choosen_stocks = choosen_stocks(3,True,8,1,-5)
print(choosen_stocks)
print('Runtime is: ',t)