import pandas as pd

from brokers.binance import Binance
from analytics.performanceAnalytics import TradeAnalysis
from playground.positionManagement import PositionManagement
from strategies.channelSlope import ChannelSlope
from strategies.vamo import Vamo
from utils.utils import time_it

'''
    strategy - strategy class with df = "Strategy(dataframe)" that has the following:
    set_random_vals() - set-up random values for Monte-Carlo
'''


class Backtest:

    def __init__(self, strategy):
        self.strategy = strategy  # <= strategy class
        self.PM = PositionManagement(strategy)
        self.statistics_dataframe = pd.DataFrame(
            columns=['Timestamp', 'Signal', 'Price', 'Amount', 'Close Profit', 'Total Profit'])

    def set_custom_params(self, params):
        self.PM.max_amount, \
        self.PM.max_positions, \
        self.PM.stop_loss, \
        self.PM.take_profit, \
        self.PM.lot_one, \
        self.PM.lot_two, \
        self.PM.lot_three = params

    """iterate thru dataframe and add the last row of initial dataframe to a new one
    while applying all the indicators and identifying entry points"""

    def run_live_simulation(self):
        source_df = self.strategy.dataframe
        destination_df = pd.DataFrame(columns=source_df.columns)
        max_rows = 60
        # loop through each row in the source DataFrame and transfer it to the destination DataFrame
        for i, row in source_df.iterrows():
            # append the row to the destination DataFrame
            destination_df = pd.concat([destination_df, row.to_frame().T], ignore_index=True)
            # check if the number of rows in destination_df exceeds max_rows
            if len(destination_df) > max_rows:
                destination_df = destination_df.iloc[1:]
            if len(destination_df) == max_rows:
                self.PM.apply_strategy(destination_df)
                self.statistics_dataframe = self.PM.statistics_dataframe
        # return total profit for optimize.minimize
        return self.PM.total_profit

    def run_static_simulation(self):
        try:
            """backtest itself"""
            self.strategy.run_test()
        except:
            pass

    def live_simulation(self):
        self.run_live_simulation()

    def static_simulation(self):
        self.run_static_simulation()

    def run_backtest(self, method=None):
        if method not in ['static_simulation', 'live_simulation']:
            raise ValueError("Invalid method specified. Use 'static_simulation' or 'live_simulation'.")
        else:
            getattr(self, method)()


''' obj - is DataStream object (eth, shib, etc.)'''


def backtest_strategy(obj, simulation_type='live', strategy=ChannelSlope):
    # Pass the DataStream obj to the strategy class
    apply_strategy = strategy(obj)
    # set random custom values of the strategy
    params = [-15, 22, 0.35, 0.32, 0, 6, 10]
    #apply_strategy.set_custom_vals_opt(params)
    # Pass strategy to backtest
    apply_backtest = Backtest(apply_strategy)
    # set random custom values of the money/pos management
    # optimized: [15000, 3, 0.985, 1.1, 5, 1, 1]
    # prod test: [220, 1, 0.985, 1.1, 0.1, 0.1, 0.1]
    vals = [200, 2, 0.985, 1.1, 0.05, 0.02, 0.1]
    #apply_backtest.set_custom_params(vals)

    # Run the backtest with the appropriate method
    apply_backtest.run_live_simulation()
    # Run the analytics
    performance = apply_backtest.statistics_dataframe
    analysis = TradeAnalysis(performance)

    analysis.modify_df()
    print(analysis.df.to_string())
    print(analysis.report())


@time_it
def main():
    SYMBOL = 'ETHUSD'
    LIMIT = '1000'
    TIMEFRAME = '1h'
    # time YYYY,M,D

    START_TIME = '2023-1-1'
    END_TIME = '2023-4-18'  # optional

    eth_test = Binance(SYMBOL, TIMEFRAME, LIMIT, START_TIME, END_TIME)
    backtest_strategy(eth_test, 'live')

    return


if __name__ == '__main__':
    main()
