"""
indicators that are not available in any lib will be stored there
"""
from datetime import datetime

import pandas as pd
import statsmodels.api as sm
import numpy as np
from finta import TA

from scipy.stats import linregress

np.seterr(divide='ignore', invalid='ignore')


class Indicators:

    @staticmethod
    def local_min_max(df):
        df['loc_min'] = df.Close[(df.Close.shift(1) > df.Close) & (df.Close.shift(-1) > df.Close)]
        df['loc_max'] = df.Close[(df.Close.shift(1) < df.Close) & (df.Close.shift(-1) < df.Close)]
        return df

    @staticmethod
    def local_min_max_gpt(df):
        df['loc_min'] = df.Close[(df.Close.shift(1) > df.Close) & (df.Close.shift(-1) > df.Close)]
        df['loc_max'] = df.Close[(df.Close.shift(1) < df.Close) & (df.Close.shift(-1) < df.Close)]
        # Handle the last candle separately
        if df.Close.iloc[-1] > df.Close.iloc[-2]:
            df.loc[df.index[-1], 'loc_max'] = df.Close.iloc[-1]
        elif df.Close.iloc[-1] < df.Close.iloc[-2]:
            df.loc[df.index[-1], 'loc_min'] = df.Close.iloc[-1]
        return df

    # To find a slope of price line
    # series - dataframe 'close' indSlope(df['close'],5)
    # n - num of kandels, 5 by default

    @staticmethod
    def slope_of_price_line(series: pd.Series, n: int) -> float:
        # Get the close prices of the last n candles
        close_prices = series[-n:]
        # Create a list of indices for the last n candles
        indices = np.arange(len(close_prices))
        # Calculate the linear regression of the close prices
        slope, intercept, r_value, p_value, std_err = linregress(indices, close_prices)
        return slope

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

    @staticmethod
    def indSlope_gpt(series: pd.Series, n):
        array_sl = [None for _ in range(n - 1)]
        for j in range(n, len(series) + 1):
            y = series[j - n:j].to_numpy()
            x = np.array(range(n))
            x_sc = (x - np.amin(x)) / (np.amax(x) - np.amin(x))
            y_sc = (y - np.amin(y)) / (np.amax(y) - np.amin(y))
            x_sc = sm.add_constant(x_sc)
            model = sm.OLS(y_sc, x_sc)
            results = model.fit()
            array_sl.append(results.params[-1])
        slope_angle = [np.rad2deg(np.arctan(sl)) if sl is not None else None for sl in array_sl]
        return np.array(slope_angle)

    # generate data frame with all needed data:
    # slope
    # channel_max
    # channel_min
    # position_in_channel
    # DF - dataframe

    @staticmethod
    def calculate_rsi(data, window):
        delta = data.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @classmethod
    def prepareDF(cls, df, atr_period: int = 14, maxmin_period: int = 10,
                  slope_period: int = 5):  # <====try to optimize
        df = cls.local_min_max(df)
        df['slope'] = cls.indSlope(df['Close'], slope_period)  # <====try to optimize
        df['ch_max'] = df['High'].rolling(maxmin_period).max()  # <====try to optimize
        df['ch_min'] = df['Low'].rolling(maxmin_period).min()  # <====try to optimize
        df['pos_in_ch'] = (df['Close'] - df['ch_min']) / (df['ch_max'] - df['ch_min'])
        df['rsi'] = cls.calculate_rsi(df['Close'], slope_period)
        df = df.reset_index()
        return df

    @staticmethod
    def aroon_indicator(data, lookback_period: int = 14):
        # Calculate the Aroon Up and Aroon Down
        aroon_up = 100 * (
                    lookback_period - data['High'].rolling(window=lookback_period).apply(np.argmax)) / lookback_period
        aroon_down = 100 * (
                    lookback_period - data['Low'].rolling(window=lookback_period).apply(np.argmin)) / lookback_period

        # Add Aroon Up and Aroon Down to the data DataFrame
        data['Aroon_Up'] = aroon_up
        data['Aroon_Down'] = aroon_down

        return data

    @staticmethod
    def parabolic_sar_daily(df):
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.set_index('Timestamp')

        # Resample the dataframe to daily data
        daily_df = df.resample('1D').agg({'High': 'max', 'Low': 'min', 'Open': 'first', 'Close': 'last', 'Volume': 'sum'})

        # Calculate the Parabolic SAR for the daily data
        daily_df['Parabolic_SAR_daily'] = TA.SAR(daily_df)

        # Drop the NaN values
        daily_df = daily_df.dropna()

        # Create a temporary dataframe with only the date (without time) and the Parabolic SAR value
        temp_df = daily_df[['Parabolic_SAR_daily']].copy()
        temp_df.index = temp_df.index.normalize()  # Normalize the index to only have the date

        # Merge the daily Parabolic SAR values back to the 30-minute dataframe
        df = df.merge(temp_df, left_on=df.index.normalize(), right_index=True, how='left')

        # Rename the merged column to 'Daily_Parabolic_SAR'
        df = df.reset_index()
        return df


    @classmethod
    def prepareDF_gpt(cls, df, rsi_period: int = 14, maxmin_period: int = 10,
                      slope_period: int = 5):  # <====try to optimize

        df = df.reset_index()
        df = cls.parabolic_sar_daily(df)
        df = cls.aroon_indicator(df)
        df = cls.local_min_max_gpt(df)

        df['Parabolic_SAR'] = TA.SAR(df)

        df['slope'] = cls.indSlope_gpt(df['Close'], slope_period)  # <====try to optimize
        df['ch_max'] = df['High'].rolling(maxmin_period).max()  # <====try to optimize
        df['ch_min'] = df['Low'].rolling(maxmin_period).min()  # <====try to optimize

        df['pos_in_ch'] = (df['Close'] - df['ch_min']) / (df['ch_max'] - df['ch_min'])

        df['slow_ma'] = TA.SMA(df, 20)
        df['fast_ma'] = TA.SMA(df, 50)
        df['MA_diff'] = df['fast_ma'] - df['slow_ma']

        df['MACD_per'] = df['MA_diff'] / df['Close']

        df = df.drop(columns=['slow_ma', 'fast_ma', 'ch_min', 'ch_max', 'MA_diff'])
        return df




'''
price_data = pd.Series([103, 104, 106, 107, 109])

n = 4
slope = Indicators.slope_of_price_line(price_data, n)
print("Slope of the price line for the last {} candles: {:.2f}".format(n, slope))

slope = Indicators.indSlope(price_data, n)
print('old one:',slope)

slope = Indicators.indSlope_gpt(price_data, n)
print("gpt:", slope)


def calculate_slope(price_data, n):
    slope = (price_data - price_data.shift(n)) / n
    return slope

slope = calculate_slope(price_data, n)
print("gpt simple:", slope)

'''
