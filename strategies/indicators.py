"""
indicators that are not available in any lib will be stored there
"""
import pandas as pd
import statsmodels.api as sm
import numpy as np
from finta import TA

np.seterr(divide='ignore', invalid='ignore')


class Indicators:

    @staticmethod
    def local_min_max(df):
        df['loc_min'] = df.close[(df.close.shift(1) > df.close) & (df.close.shift(-1) > df.close)]
        df['loc_max'] = df.close[(df.close.shift(1) < df.close) & (df.close.shift(-1) < df.close)]
        return df

    # To find a slope of price line
    # series - dataframe 'close' indSlope(df['close'],5)
    # n - num of kandels, 5 by default

    @staticmethod
    def indSlope(series: pd.Series, n):
        array_sl = [j * 0 for j in range(n - 1)]
        for j in range(n, len(series) + 1):
            y = series[j - n:j].to_numpy()
            x = np.array(range(n))
            x_sc = (x - np.amin(x)) / (np.amax(x) - np.amin(x))
            y_sc = (y - np.amin(y)) / (np.amax(y) - np.amin(y))
            x_sc = sm.add_constant(x_sc)
            model = sm.OLS(y_sc, x_sc)
            results = model.fit()
            array_sl.append(results.params[-1])
        slope_angle = (np.rad2deg(np.arctan(np.array(array_sl))))
        return np.array(slope_angle)

    # generate data frame with all needed data:
    # slope
    # channel_max
    # channel_min
    # position_in_channel
    # DF - dataframe

    @classmethod
    def prepareDF(cls, df, atr_period: int = 14, maxmin_period: int = 10,
                  slope_period: int = 5):  # <====try to optimize
        df = cls.local_min_max(df)
        df['ATR'] = TA.ATR(df, atr_period)  # <====try to optimize
        df['slope'] = cls.indSlope(df['close'], slope_period)  # <====try to optimize
        df['ch_max'] = df['high'].rolling(maxmin_period).max()  # <====try to optimize
        df['ch_min'] = df['low'].rolling(maxmin_period).min()  # <====try to optimize
        df['pos_in_ch'] = (df['close'] - df['ch_min']) / (df['ch_max'] - df['ch_min'])
        df = df.reset_index()
        return df
