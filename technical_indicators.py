import pandas as pd
from ta import momentum, trend

from price_action_data import get_minute_data


def add_ema_col(df: pd.DataFrame, period=20):
    """
    Exponential moving average calculator.
    :param df: price action DataFrame
    :param period: EMA length
    :return: list of EMA values
    """
    d = {
        'ema': trend.ema_indicator(df.close, window=period)
    }

    df1 = pd.DataFrame(d)

    df.dropna(inplace=True)

    return pd.concat([df, df1], axis=1)


def add_rsi_col(df: pd.DataFrame, period=14):
    """
    Calculates Stochastic RSI against price action data and applies values to data frame
    :param df: Provided data frame
    :param period: RSI period
    :return: updated DataFrame with RSI values
    """
    # Adding to existing dataframe returns an empty dataframe, so a work-around is to create a new DF and concatenate
    # both together
    d = {
        'rsi': momentum.rsi(df.close, window=period),
    }

    df1 = pd.DataFrame(d)

    df.dropna(inplace=True)

    return pd.concat([df, df1], axis=1)


def add_macd_diff_col(df: pd.DataFrame):
    """
    Calculates MACD difference for each row and adds the result of each to a new column.
    :param df: Provided DataFrame
    :return: updated DataFrame with new MACD values
    """
    d = {
        'macd': trend.macd_diff(df.close)
    }

    df1 = pd.DataFrame(d)

    df.dropna(inplace=True)

    return pd.concat([df, df1], axis=1)
