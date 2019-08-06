#!/usr/bin/env python3
# coding:utf-8
import futu as ft
import time
import pync

# 监控股票
stock = ['SH.000001']
# 告警价格
strategy = [
   2760
]

def menuNotify(message):
    pync.notify(message, title='系统通知', appIcon="notify.png")

def notify(stock):
    _stock = "股票代码:%s, 交易时间:%s, 现价:%.3f, 开盘价:%.3f, 最高价:%.3f, 最低价:%.3f, 成交量:%d万股, 成交额:%.3f万元, 换手率:%.2f" % (
        stock.code.values[0], stock.data_time.values[0], stock.last_price,
        stock.open_price, stock.high_price, stock.low_price,
        stock.volume.values[0] / 10000, stock.turnover / 10000, stock.turnover_rate
    )
    # 监控
    for price in strategy:
        if stock.last_price.values[0] > price:
            m = "时间:%s, 价格:%.2f, 交易量:%d万" % (stock.data_time.values[0], stock.last_price.values[0], stock.volume.values[0]/10000)
            menuNotify(m)
    # 终端输出
    print(_stock)

# 回调逻辑处理
class StockQuoteMonitor(ft.StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(StockQuoteMonitor, self).on_recv_rsp(rsp_str)
        if ret_code != ft.RET_OK:
            print("StockQuoteMonitor: error, msg: %s" % data)
            return ft.RET_ERROR, data
        notify(data)
        return ft.RET_OK, data

# 实例化行情上下文对象
quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)

# 上下文控制
# 开启异步数据接收
quote_ctx.start()

# 设置用于异步处理数据的回调对象(可派生支持自定义)
quote_ctx.set_handler(ft.TickerHandlerBase())

# 注册实时报价handder
quote_ctx.set_handler(StockQuoteMonitor())

# 实时报价
quote_ctx.subscribe(stock, [ft.SubType.QUOTE])

while True:
    time.sleep(15)
    t = time.strftime("%H", time.localtime())
    t = int(t)
    # A股交易时间: 9:30 - 11:30, 13:00 - 15:00
    # 根据具体需求调整
    if t > 15 or t < 9:
        print("未开市\n")
        break

# 停止异步数据接收
quote_ctx.stop()
# 关闭对象
quote_ctx.close()
