"""
indicators that are not available in any lib will be stored there
"""
import pandas as pd
import statsmodels.api as sm
import numpy as np
from finta import TA


from scipy.stats import linregress

np.seterr(divide='ignore', invalid='ignore')


class Indicators:

    @staticmethod
    def local_min_max(df):
        df['loc_min'] = df.close[(df.close.shift(1) > df.close) & (df.close.shift(-1) > df.close)]
        df['loc_max'] = df.close[(df.close.shift(1) < df.close) & (df.close.shift(-1) < df.close)]
        return df

    @staticmethod
    def local_min_max_gpt(df):
        df['loc_min'] = df.close[(df.close.shift(1) > df.close) & (df.close.shift(-1) > df.close)]
        df['loc_max'] = df.close[(df.close.shift(1) < df.close) & (df.close.shift(-1) < df.close)]
        # Handle the last candle separately
        if df.close.iloc[-1] > df.close.iloc[-2]:
            df.loc[df.index[-1], 'loc_max'] = df.close.iloc[-1]
        elif df.close.iloc[-1] < df.close.iloc[-2]:
            df.loc[df.index[-1], 'loc_min'] = df.close.iloc[-1]
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
        df['ATR'] = TA.ATR(df, atr_period)  # <====try to optimize
        df['slope'] = cls.indSlope(df['close'], slope_period)  # <====try to optimize
        df['ch_max'] = df['high'].rolling(maxmin_period).max()  # <====try to optimize
        df['ch_min'] = df['low'].rolling(maxmin_period).min()  # <====try to optimize
        df['pos_in_ch'] = (df['close'] - df['ch_min']) / (df['ch_max'] - df['ch_min'])
        df = df.reset_index()
        return df

    @classmethod
    def prepareDF_gpt(cls, df, atr_period: int = 14, maxmin_period: int = 10,
                  slope_period: int = 5):  # <====try to optimize
        df = cls.local_min_max_gpt(df)
        df['ATR'] = TA.ATR(df, atr_period)  # <====try to optimize
        df['slope'] = cls.indSlope_gpt(df['close'], slope_period)  # <====try to optimize
        #df = cls.linear_regression_channel(df, maxmin_period)

        df['ch_max'] = df['high'].rolling(maxmin_period).max()  # <====try to optimize
        df['ch_min'] = df['low'].rolling(maxmin_period).min()  # <====try to optimize

        df['pos_in_ch'] = (df['close'] - df['ch_min']) / (df['ch_max'] - df['ch_min'])
        df['rsi'] = cls.calculate_rsi(df['close'], slope_period)
        df = df.reset_index()

        return df

    @classmethod
    def linear_regression_channel(cls, data, window):
        # check if data and window parameters are valid
        if not isinstance(data, pd.DataFrame):
            raise TypeError("The 'data' parameter must be a pandas DataFrame.")
        if not isinstance(window, int) or window < 1:
            raise ValueError("The 'window' parameter must be a positive integer.")

        # check if the data has enough rows for the window size
        if len(data) < window:
            raise ValueError("The 'data' parameter has fewer rows than the window size.")

        # drop any rows with missing or invalid data
        data = data.dropna()

        # calculate the x values for the regression line
        x = np.arange(window)

        # loop through each window in the data and calculate the channel values
        upper_channel_values = []
        lower_channel_values = []
        for i in range(len(data) - window + 1):
            y = data['close'][i:i + window].values
            slope, intercept, _, _, _ = linregress(x, y)
            regression_line = slope * x + intercept

            upper_channel = regression_line + (data['high'][i:i + window] - regression_line).max()
            lower_channel = regression_line - (regression_line - data['low'][i:i + window]).max()

            upper_channel_values.append(upper_channel[-1])
            lower_channel_values.append(lower_channel[-1])

        # create Series from channel values with explicit float64 dtype
        upper_channel_series = pd.Series(upper_channel_values, dtype=np.float64, index=data.index[window - 1:])
        lower_channel_series = pd.Series(lower_channel_values, dtype=np.float64, index=data.index[window - 1:])

        # add the channel values to the data DataFrame
        data['ch_max'] = upper_channel_series
        data['ch_min'] = lower_channel_series

        return data

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




