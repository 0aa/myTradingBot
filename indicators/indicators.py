"""
indicators that are not available in any lib will be stored there
"""

import statsmodels.api as sm
import numpy as np
from finta import TA


class Indicators:

    # find local minimum / local maximum
    def isLCC(self, df, i):
        LCC = 0
        if df['close'][i] <= df['close'][i + 1] and df['close'][i] <= df['close'][i - 1] < df['close'][i + 1]:
            # local low
            LCC = i - 1
        return LCC

    def isHCC(self, df, i):
        HCC = 0
        if df['close'][i] >= df['close'][i + 1] and df['close'][i] >= df['close'][i - 1] > df['close'][i + 1]:
            # local max
            HCC = i
        return HCC

    def getMaxMinChannel(self, DF, n):
        maxx = 0
        minn = DF['low'].max()
        for i in range(1, n):
            if maxx < DF['high'][len(DF) - i]:
                maxx = DF['high'][len(DF) - i]
            if minn > DF['low'][len(DF) - i]:
                minn = DF['low'][len(DF) - i]
        return maxx, minn

    # True Range and Average True Range indicator
    def indATR(self, source_df, n):
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
    def indSlope(self, series, n):
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
    def PrepareDF(self, DF, atr_period=14):
        ohlc = DF.iloc[:, [0, 1, 2, 3, 4]]
        ohlc.columns = ["timestamp", "open", "high", "low", "close"]
        ohlc = ohlc.set_index('timestamp')
        df = self.indATR(ohlc, atr_period).reset_index()  # <====try to optimize
        df['slope'] = self.indSlope(df['close'], 5)  # <====try to optimize
        df['channel_max'] = df['high'].rolling(10).max()  # <====try to optimize
        df['channel_min'] = df['low'].rolling(10).min()  # <====try to optimize
        df['position_in_channel'] = (df['close'] - df['channel_min']) / (df['channel_max'] - df['channel_min'])
        df = df.set_index('timestamp')
        df = df.reset_index()
        return df
