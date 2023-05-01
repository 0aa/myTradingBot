from datetime import datetime, timedelta

import pandas as pd
from finviz.screener import Screener


from analytics.performanceAnalytics import TradeAnalysis
from backtest.backtest import Backtest
from strategies.ripsterClouds import ripsterClouds

from pandas_datareader import data as pdr
import yfinance as yf

yf.pdr_override()



class YahooData:
    def __init__(self, symbol, interval, start_date=None, end_date=None):
        """
        :Parameters:
            period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
            timeframe : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
            start_date: str
                Download start date string (YYYY-MM-DD) or _datetime, inclusive.
                Default is 1900-01-01
                E.g. for start="2020-01-01", the first data point will be on "2020-01-01"
            end_date: str
                Download end date string (YYYY-MM-DD) or _datetime, exclusive.
                Default is now
                E.g. for end="2023-01-01", the last data point will be on "2022-12-31"


        self.stock = yf.Ticker(symbol)
        self.dataframe = self.stock.history(period=period, interval=timeframe)
        """
        self.symbol = symbol
        self.interval = interval
        self.dataframe = pdr.get_data_yahoo(self.symbol, start=start_date, end=end_date, interval=self.interval)

        self.dataframe.reset_index(inplace=True)
        self.dataframe.rename(columns={'Datetime' : 'Timestamp'}, inplace=True)
        self.dataframe = self.dataframe[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]

    def get_unlimited_klines(self, start_date, end_date):
        """
        tickers : str, list
            List of tickers to download
        period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
        start: str
            Download start date string (YYYY-MM-DD) or _datetime, inclusive.
            Default is 1900-01-01
            E.g. for start="2020-01-01", the first data point will be on "2020-01-01"
        end: str
            Download end date string (YYYY-MM-DD) or _datetime, exclusive.
            Default is now
            E.g. for end="2023-01-01", the last data point will be on "2022-12-31"
        """
        # Download historical data using yfinance

        dataframe = pdr.get_data_yahoo(self.symbol, start=start_date, end=end_date, interval=self.interval)

        dataframe.reset_index(inplace=True)
        dataframe.rename(columns={'Datetime' : 'Timestamp'}, inplace=True)
        dataframe = dataframe[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]


        self.dataframe = dataframe
        return dataframe



def backtest_strategy(broker, simulation_type='live', strategy=ripsterClouds):
    apply_strategy = strategy(broker)

    # Pass strategy to backtest
    apply_backtest = Backtest(apply_strategy)


    max_investments = 1000
    avg_price = broker.dataframe['Close'].iloc[-1]
    lot_size = (max_investments / avg_price) * 0.9


    position_vals = [max_investments, 100, 0.9, 20, lot_size, 1, 1]
    apply_backtest.set_custom_params(position_vals)

    # Run the backtest with the appropriate method
    apply_backtest.run_live_simulation()
    # Run the analytics
    performance = apply_backtest.statistics_dataframe
    analysis = TradeAnalysis(performance, position_vals)

    analysis.modify_df()
    print(analysis.df.to_string())
    print(analysis.report())
    return performance['Close Profit'].sum()

def screener():
    filters = ['sh_price_u50', 'ta_highlow20d_nh', 'ta_perf_4w10o', 'ta_perf2_52wup', 'ta_sma20_pa', 'ta_sma50_pa']  # Shows companies in NASDAQ which are in the S&P500
    return Screener(filters=filters, table='Performance',
                          order='price')  # Get the performance table and sort it by price ascending


if __name__ == "__main__":


    SYMBOL = 'AFIB'
    START_TIME = '2023-3-1'
    END_TIME = '2023-4-1'

    TIMEFRAME = '1h'
    """
    total_profit = 0
    tickers = screener()
    print(len(tickers))
    for ticker in tickers:
        stock = YahooData(symbol=ticker['Ticker'], interval=TIMEFRAME, start_date=START_TIME, end_date=END_TIME)
        profit = backtest_strategy(stock, 'live', ripsterClouds)
        total_profit += profit
    print("total profit", total_profit)
    """
    stock = YahooData(symbol=SYMBOL, interval=TIMEFRAME, start_date=START_TIME, end_date=END_TIME)
    profit = backtest_strategy(stock, 'live', ripsterClouds)



