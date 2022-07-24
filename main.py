import datetime as dt
import time

import binance

from technical_indicators import *
from price_action_data import SYS_ONLINE, get_minute_data, client, get_current_price
from trade import Trade, TradeSignal
from binance.enums import *

from db.db import *


TICKER = 'BTCUSDT'
CONN = init_conn('db/db.sqlite')


class User:
    def __init__(self, binance_client: binance.Client, sl_p=0.99, tp_p=1.0125, trade_p=0.02):
        self.client = binance_client
        self.btc_bal = 0.0
        self.usdt_bal = 0.0

        # Value of position before triggering SL
        self.sl_p = sl_p

        # Value of position before triggering TP
        self.tp_p = tp_p

        # How big the position should be relative to your account (e.g. each trade will be 2% of total asset size)
        self.trade_size_p = trade_p

    def set_btc_bal(self, bal):
        self.btc_bal = bal

    def add_btc_bal(self, amount):
        self.btc_bal += amount

    def sub_btc_bal(self, amount):
        self.btc_bal -= amount

    def set_usdt_bal(self, bal):
        self.usdt_bal = bal

    def add_usdt_bal(self, amount):
        self.usdt_bal += amount

    def sub_usdt_bal(self, amount):
        self.usdt_bal -= amount


def main():
    pa = get_minute_data(TICKER)

    pa = add_rsi_col(pa)
    pa = add_ema_col(pa)
    pa = add_macd_diff_col(pa)
    # print(pa.tail(5))
    # print(pa.iloc[-1])

    t = TradeSignal(pa)
    t.validate_signal()

    me = User(client)
    me.set_btc_bal(float(client.get_asset_balance('BTC')['free']))
    me.set_usdt_bal(float(client.get_asset_balance('USDT')['free']))

    print()
    print('======== TO BUY =======')
    to_spend = me.trade_size_p * me.usdt_bal
    print(f' to spend: ${to_spend}')
    buy_order_qty = to_spend / t.price
    print(f' buy order qty of btc: {buy_order_qty}')
    print()
    print('======== TO SELL =======')
    to_spend = me.trade_size_p * me.btc_bal
    print(f' to spend: ¢{to_spend}')
    sell_order_qty = to_spend



    print()
    print('before trade')
    print(f'    ===BTC: {me.btc_bal}')
    print(f'    ==USDT: {me.usdt_bal}')

    trade = client.create_order(
        symbol=TICKER,
        type='MARKET',
        side='BUY',
        quantity=0.001,
    )

    print(trade)

    # print(client.get_all_orders(symbol=TICKER))

    # add/remove balances
    me.add_btc_bal(float(trade['executedQty']))
    me.sub_usdt_bal(float(trade['cummulativeQuoteQty']))

    t_obj = Trade(
        trade['clientOrderId'], t.side, 'open', trade['executedQty'], trade['cummulativeQuoteQty'], me.btc_bal,
        me.usdt_bal, trade['transactTime']
    )

    execute_query(CONN, f"""
        INSERT INTO
          trades (trade_id, type, open_or_close, qty, price, btc_bal, usdt_bal, date)
        VALUES
          ('{trade['clientOrderId']}', '{t.side}', 'open', '{trade['executedQty']}',
          '{trade['cummulativeQuoteQty']}', '{me.btc_bal}', '{me.usdt_bal}', '{trade['transactTime']}')
    """)

    me.set_btc_bal(float(client.get_asset_balance('BTC')['free']))
    me.set_usdt_bal(float(client.get_asset_balance('USDT')['free']))
    print()
    print('after trade')
    print(f'    ===BTC: {me.btc_bal}')
    print(f'    ==USDT: {me.usdt_bal}')


if __name__ == '__main__':
    if not SYS_ONLINE: raise Exception('Binance system is not operating normally')

    # while True:
    #     now = dt.datetime.now().second
    #     if now == 0:
    #         print(f'price at: {(dt.datetime.now() - dt.timedelta(minutes=1)).strftime("%H:%M:%S")}')
    #         main()
    #         print()
    main()

        # test()
