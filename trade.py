import pandas as pd

# from main import TICKER
from price_action_data import client


# 20 EMA, RSI, MACD
class TradeSignal:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.side = 'BUY'  # todo change back to None after debugging

        last_pa = df.iloc[-1]
        self.price = last_pa['close']
        self.ema = last_pa['ema']
        self.rsi = last_pa['rsi']
        self.macd = last_pa['macd']

    def validate_signal(self):
        """
        Determines trade signal.
        :return: True if a buy signal, False if a sell signal and None if signal is invalid
        """
        print(f'price: {self.price}')
        # If price closed on or above 20 EMA
        if self.close_above_ema():
            print(f'PRICE CLOSED ABOVE EMA {self.ema}')

            if self.macd_cross_up():
                print('MACD CROSS UP')

                if self.rsi_above_50():
                    print(f'RSI ABOVE 50 {self.rsi}')
                    print('=========== BUY SIGNAL ==========')
                    self.side = 'BUY'
                    return True

        # Else, price closed below 20 EMA
        else:
            print('PRICE CLOSE BELOW EMA')

            if self.macd_cross_down():
                print('MACD CROSS DOWN')

                if not self.rsi_above_50():
                    print('RSI BELOW 50')
                    print('=========== SELL SIGNAL ==========')
                    self.side = 'SELL'
                    return False

        return None

    def close_above_ema(self):
        """
        Returns True if recent price closed above EMA, returns False otherwise.
        """
        return self.price >= self.ema

    def macd_cross_up(self):
        """
        Returns True if MACD has recently crossed up from 3 or more consecutive negative MACD diff.
        """
        # If most recent MACD value is positive
        if self.macd > 0.0:
            print(f'pos macd {self.macd}')
            # Get last 4 macd values
            last_4_macd = self.df.tail(4)['macd']

            # Strip the last value (we already have it, and we want to know if the previous 3 are negative)
            macd_values = last_4_macd[:-1]

            # If previous 3 MACD values before most recent are all negative (showing a cross upwards), return True
            if all(i <= 0.0 for i in macd_values):
                return True

        return False

    def macd_cross_down(self):
        """
        Returns True if MACD has recently crossed up from 3 or more consecutive negative MACD diff.
        """
        # If most recent MACD value is negative
        if self.macd < 0.0:
            print(f'neg macd {self.macd}')
            # Get last 4 macd values
            last_4_macd = self.df.tail(4)['macd']

            # Strip the last value (we already have it, and we want to know if the previous 3 are positive)
            macd_values = last_4_macd[:-1]

            # If previous 3 MACD values before most recent are all positive (showing a cross downwards), return True
            if all(i >= 0.0 for i in macd_values):
                return True

        return False

    def rsi_above_50(self):
        """
        Returns True if RSI is above 50, False otherwise
        """
        return self.rsi > 50.0


class User:
    def __init__(self, binance_client, sl_p=0.99, tp_p=1.0125, trade_p=0.02):
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


class Trade:
    def __init__(self, trade_id, trade_type, open_or_close, qty, price, btc_bal, usdt_bal, date):
        self.id = None
        self.trade_id = trade_id
        self.type = trade_type
        self.open_or_close = open_or_close
        self.qty = qty
        self.price = price
        self.btc_bal = btc_bal
        self.usdt_bal = usdt_bal
        self.date = date


def get_pos_size(user: User, side, price):
    if 'BUY' in side:
        return (user.trade_size_p * user.usdt_bal) / price

    return user.trade_size_p * user.btc_bal


def execute_trade(user: User, side, quantity):
    return user.client.create_order(
        symbol='BTCUSDT',
        type='MARKET',
        side=side,
        quantity=quantity,
    )


def save_trade_data(conn, trade, side, open_or_close, btc_bal, usdt_bal):
    pass
