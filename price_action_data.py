from binance.client import Client
import pandas as pd

API_KEY = 'hKjUJgB0DVaAdMgS3ZDrtgeReGyITNqgLZRwQmV4RxI4TIQYOUGwXE0q0VRKrvug'
SECRET_KEY = 'MBtRZSzlZ8U7WUsMDcTzr5p18hlNW3aCMCu24lxxKVS9xLDG1O0eU5xaNCytisJh'

client = Client(API_KEY, SECRET_KEY, testnet=True)

SYS_ONLINE = True if client.get_system_status()['status'] == 0 else False


KLINE_COLUMNS = ['time', 'open', 'high', 'low', 'close', 'vol']


def get_current_price(ticker: str) -> float:
    """
    Gets most up-to-date price of given ticker
    :return: price as a float
    """
    price = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE, limit=1)

    return float(price[0][4])


def get_minute_data(ticker: str, limit=101) -> pd.DataFrame:
    """
    Retrieves the minute price action data for given ticker.
    :param ticker: Given ticker
    :param limit: How many minutes should the data go back (default 2hrs)
    :return: DataFrame
    """

    # Retrieve minute data
    df = pd.DataFrame(client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE, limit=limit))

    # Trim to first 6 columns
    df = df.iloc[:, :6]

    # Set columns
    df.columns = KLINE_COLUMNS

    # Set index and data type of DataFrame
    df = df.set_index('time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)

    return df.iloc[:-1]
