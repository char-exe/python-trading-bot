import datetime as dt
import time

import binance

from technical_indicators import *
from price_action_data import SYS_ONLINE, get_minute_data, client, get_current_price
from trade import Trade, TradeSignal, get_pos_size, execute_trade, save_trade_data
# from binance.enums import *

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

    t_obj = Trade(
        trade['clientOrderId'], t.side, 'open', trade['executedQty'], trade['cummulativeQuoteQty'], me.btc_bal,
        me.usdt_bal, trade['transactTime']
    )
    me.set_btc_bal(float(client.get_asset_balance('BTC')['free']))
    me.set_usdt_bal(float(client.get_asset_balance('USDT')['free']))
    execute_query(CONN, f"""
        INSERT INTO
          trades (trade_id, type, open_or_close, qty, price, btc_bal, usdt_bal, date)
        VALUES
          ('{trade['clientOrderId']}', '{t.side}', 'open', '{trade['executedQty']}',
          '{trade['cummulativeQuoteQty']}', '{me.btc_bal}', '{me.usdt_bal}', '{trade['transactTime']}')
    """)


    print()
    print('after trade')
    print(f'    ===BTC: {me.btc_bal}')
    print(f'    ==USDT: {me.usdt_bal}')

def init_data():
    pa = get_minute_data(TICKER)
    pa = add_rsi_col(pa)
    pa = add_ema_col(pa)
    pa = add_macd_diff_col(pa)
    return TradeSignal(pa)

def init_user():
    usr = User(client)
    usr.set_btc_bal(float(client.get_asset_balance('BTC')['free']))
    usr.set_usdt_bal(float(client.get_asset_balance('USDT')['free']))
    return usr

if __name__ == '__main__':
    if not SYS_ONLINE: raise Exception('Binance system is not operating normally')
    me = init_user()

    while True:
        sec = dt.datetime.now().second
        if sec == 0:
            print(f'price at: {(dt.datetime.now() - dt.timedelta(minutes=1)).strftime("%H:%M:%S")}')
            ts = init_data()
            side = ts.validate_signal()
            if side:
                quant = get_pos_size(user=me, side=side, price=ts.price)
                trade = execute_trade(user=me, side=side, quantity=quant)

                me.set_btc_bal(float(client.get_asset_balance('BTC')['free']))
                me.set_usdt_bal(float(client.get_asset_balance('USDT')['free']))

                save_trade_data(me, CONN, trade, side, 'open', me.btc_bal, me.usdt_bal)

                target_price = ts.price * me.tp_p
                stop_loss = ts.price * me.sl_p
                pos_open = True
                while pos_open:
                    price = float(get_current_price(TICKER))
                    print(price)
                    print(target_price)
                    print()
                    time.sleep(1)

        # test()
