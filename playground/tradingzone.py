from datetime import datetime
import numpy as np
from finta import TA
import matplotlib.pyplot as plt

from brokers.binance import Binance


class Tradingzone:

    @staticmethod
    def fibonacci_retracement_levels(data):
        high = data['High'].max()
        low = data['Low'].min()
        difference = high - low
        levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        return [high - level * difference for level in levels]

    @staticmethod
    def pivot_points(data):
        high = data['High'].max()
        low = data['Low'].min()
        close = data['Close'].iloc[-1]
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        return [s2, s1, pivot, r1, r2]

    @staticmethod
    def trend_indicators(data):
        data['SMA_20'] = TA.SMA(data, 20)
        data['SMA_50'] = TA.SMA(data, 50)
        macd = TA.MACD(data)
        data['MACD'] = macd['MACD']
        data['MACD_signal'] = macd['SIGNAL']
        data['Parabolic_SAR'] = TA.SAR(data)
        return data

    @staticmethod
    def volatility_indicators(data):
        b_bands = TA.BBANDS(data)
        data['BB_lower'], data['BB_middle'], data['BB_upper'] = b_bands['BB_LOWER'], b_bands['BB_MIDDLE'], b_bands[
            'BB_UPPER']
        data['ATR'] = TA.ATR(data)
        return data

    @staticmethod
    def momentum_indicators(data):
        data['RSI'] = TA.RSI(data)
        data['Stoch_K'], data['Stoch_D'] = TA.STOCH(data), TA.STOCHD(data)
        return data

    @staticmethod
    def volume_indicators(data):
        data['OBV'] = TA.OBV(data)
        data['ADL'] = TA.ADL(data)
        return data

    @staticmethod
    def support_resistance_levels(data):
        # Calculate Fibonacci Retracement levels
        fibonacci_levels = Tradingzone.fibonacci_retracement_levels(data)
        data['Fibonacci_Level'] = np.nan
        for level in fibonacci_levels:
            data.loc[abs(data['Close'] - level) < 0.01 * data['Close'], 'Fibonacci_Level'] = level

        # Calculate Pivot Points
        pivot_points_levels = Tradingzone.pivot_points(data)
        data['Pivot_Point_Level'] = np.nan
        for level in pivot_points_levels:
            data.loc[abs(data['Close'] - level) < 0.01 * data['Close'], 'Pivot_Point_Level'] = level
        return data

    @staticmethod
    def calculate_long_entry_points(data):
        data['buy_zone'] = 0

        # Trend Indicators
        data.loc[data['SMA_20'] > data['SMA_50'], 'buy_zone'] += 1  # Golden cross
        data.loc[data['MACD'] > data['MACD_signal'], 'buy_zone'] += 1  # Positive MACD crossover
        data.loc[data['Parabolic_SAR'] > data['Close'], 'buy_zone'] += 1  # Price below Parabolic SAR

        # Volatility Indicators
        data.loc[data['Close'] < data['BB_lower'], 'buy_zone'] += 1  # Price below the lower Bollinger Band
        data.loc[data['ATR'] < 0.02 * data['Close'], 'buy_zone'] += 1  # ATR less than 2% of price

        # Momentum Indicators
        data.loc[data['RSI'] < 30, 'buy_zone'] += 1  # Oversold RSI
        data.loc[data['Stoch_K'] > data['Stoch_D'], 'buy_zone'] += 1  # Bullish Stochastic crossover

        # Volume Indicators
        data.loc[data['OBV'] > data['OBV'].shift(1), 'buy_zone'] += 1  # Increasing On-Balance Volume
        data.loc[data['ADL'] > data['ADL'].shift(1), 'buy_zone'] += 1  # Increasing Accumulation/Distribution Line

        # Support and Resistance Levels
        data.loc[data['Fibonacci_Level'].notna(), 'buy_zone'] += 1  # Near Fibonacci support level
        data.loc[data['Pivot_Point_Level'].notna(), 'buy_zone'] += 1  # Near Pivot Point support level

        return data

    @staticmethod
    def calculate_short_exit_points(data):
        data['sell_zone'] = 0

        # Trend Indicators
        data.loc[data['SMA_20'] < data['SMA_50'], 'sell_zone'] += 1  # Death cross
        data.loc[data['MACD'] < data['MACD_signal'], 'sell_zone'] += 1  # Negative MACD crossover
        data.loc[data['Parabolic_SAR'] < data['Close'], 'sell_zone'] += 1  # Price above Parabolic SAR

        # Volatility Indicators
        data.loc[data['Close'] > data['BB_lower'], 'sell_zone'] += 1  # Price above the upper Bollinger Band
        data.loc[data['ATR'] > 0.02 * data['Close'], 'sell_zone'] += 1  # ATR greater than 2% of price

        # Momentum Indicators
        data.loc[data['RSI'] > 70, 'sell_zone'] += 1  # Overbought RSI
        data.loc[data['Stoch_K'] < data['Stoch_D'], 'sell_zone'] += 1  # Bearish Stochastic crossover

        # Volume Indicators
        data.loc[data['OBV'] < data['OBV'].shift(1), 'sell_zone'] += 1  # Decreasing On-Balance Volume
        data.loc[data['ADL'] < data['ADL'].shift(1), 'sell_zone'] += 1  # Decreasing Accumulation/Distribution Line

        # Support and Resistance Levels
        data.loc[data['Fibonacci_Level'].notna(), 'sell_zone'] += 1  # Near Fibonacci resistance level
        data.loc[data['Pivot_Point_Level'].notna(), 'sell_zone'] += 1  # Near Pivot Point resistance level

        return data

    @staticmethod
    def drop_unnecessary_columns(data):
        data = data.drop(columns=['SMA_20', 'SMA_50', 'MACD', 'MACD_signal', 'MACD_signal', 'BB_lower',
                                  'BB_middle', 'BB_upper', 'ATR', 'RSI', 'Stoch_K', 'Stoch_D',
                                  'OBV', 'ADL', 'Fibonacci_Level', 'Pivot_Point_Level', 'Parabolic_SAR'])
        return data

    @staticmethod
    def risk_zones(data):

        data.set_index('Timestamp', inplace=True)
        data = Tradingzone.trend_indicators(data)
        data = Tradingzone.volatility_indicators(data)
        data = Tradingzone.momentum_indicators(data)
        data = Tradingzone.volume_indicators(data)
        data = Tradingzone.support_resistance_levels(data)
        #  identify entry/exit zones
        data = Tradingzone.calculate_long_entry_points(data)
        data = Tradingzone.calculate_short_exit_points(data)
        #  drop indicators
        data = Tradingzone.drop_unnecessary_columns(data)

        data = data.reset_index()

        return data

    @staticmethod
    def visualize_entry_zone(data):
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, sharex=True)

        # Plot the Close price
        ax1.plot(data.index, data['Close'], label='Price')
        ax1.legend()
        ax1.set_title('Price')

        # Plot the long entry points as columns
        ax2.bar(data.index, data['long_entry_points'], label='Long Entry Points', color='green')
        ax2.legend()
        ax2.set_title('Long Entry Points')

        # Plot the long entry points as columns
        ax3.bar(data.index, data['short_exit_points'], label='Short Exit Points', color='red')
        ax3.legend()
        ax3.set_title('Short Exit Points')

        plt.show()


if __name__ == '__main__':
    SYMBOL = 'ETHUSDT'
    LIMIT = '1000'
    TIMEFRAME = '30m'
    # time YYYY,M,D
    START_TIME = int(datetime(2023, 1, 21).timestamp()) * 1000
    END_TIME = int(datetime(2023, 4, 30).timestamp()) * 1000  # optional
    # create class object with the data we need

    # create the dataframe
    eth_test = Binance(SYMBOL, TIMEFRAME, LIMIT, START_TIME, END_TIME)
    data = eth_test.dataframe

    data = Tradingzone.risk_zones(data)
