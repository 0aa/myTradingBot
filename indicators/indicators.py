"""
indicators that are not available in any lib will be stored there
"""

import statsmodels.api as sm
import numpy as np
from finta import TA


class Indicators:

    # find local minimum
    @staticmethod
    def isLCC(df, i):
        LCC = 0
        if df['close'][i] <= df['close'][i + 1] and df['close'][i] <= df['close'][i - 1] < df['close'][i + 1]:
            # local low
            LCC = i - 1
        return LCC

    # find local maximum
    @staticmethod
    def isHCC(df, i):
        HCC = 0
        if df['close'][i] >= df['close'][i + 1] and df['close'][i] >= df['close'][i - 1] > df['close'][i + 1]:
            # local max
            HCC = i
        return HCC

    @staticmethod
    def getMaxMinChannel(df, n):
        maxx = 0
        minn = df['low'].max()
        for i in range(1, n):
            if maxx < df['high'][len(df) - i]:
                maxx = df['high'][len(df) - i]
            if minn > df['low'][len(df) - i]:
                minn = df['low'][len(df) - i]
        return maxx, minn

    # True Range and Average True Range indicator
    @staticmethod
    def indATR(source_df, n):
        df = source_df.copy()
        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
        df['ATR'] = df['TR'].rolling(n).mean()
        df_temp = df.drop(['H-L', 'H-PC', 'L-PC'], axis=1)
        return df_temp

    # To find a slope of price line
    # series - dataframe 'close' indSlope(df['close'],5)
    # n - num of kandels, 5 by default
    @staticmethod
    def indSlope(series, n):
        array_sl = [j * 0 for j in range(n - 1)]
        for j in range(n, len(series) + 1):
            y = series[j - n:j]
            x = np.array(range(n))
            x_sc = (x - x.min()) / (x.max() - x.min())
            y_sc = (y - y.min()) / (y.max() - y.min())
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
    def PrepareDF(cls, df, atr_period=14, maxmin_period=10,slope_period=5):   # <====try to optimize
        ohlc = df.iloc[:, [0, 1, 2, 3, 4]]
        ohlc.columns = ["timestamp", "open", "high", "low", "close"]
        ohlc = ohlc.set_index('timestamp')
        df = cls.indATR(ohlc, atr_period).reset_index()  # <====try to optimize
        df['slope'] = cls.indSlope(df['close'], slope_period)  # <====try to optimize
        df['channel_max'] = df['high'].rolling(maxmin_period).max()  # <====try to optimize
        df['channel_min'] = df['low'].rolling(maxmin_period).min()  # <====try to optimize
        df['position_in_channel'] = (df['close'] - df['channel_min']) / (df['channel_max'] - df['channel_min'])
        df = df.set_index('timestamp')
        df = df.reset_index()
        return df
