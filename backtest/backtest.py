from multiprocessing import Pool
import pandas as pd
from main import TradingBot
from strategies.channel_slope import ChannelSlope

'''
    obj - strategy class with df = "Strategy(dataframe)" that has the following:
    set_random_vals() - set-up random values for Monte-Carlo
    num_runs - number of iterations
'''


class Backtest:

    def __init__(self, obj):
        self.obj = obj  # <= strategy class
        self.num_runs = 1
        self.montecarlo = False
        self.position = None
        self.total_profit = 0
        self.num_positions = 4  # maximum number of positions that can be open simultaneously
        self.positions = []  # list of currently open positions

    def apply_strategy(self, destination_df):
        try:
            signal = self.obj.run(destination_df)
            current_price = destination_df['close'].iloc[-1]
            if signal == 'BUY__':
                if self.position is None and len(self.positions) < self.num_positions:
                    self.positions.append(current_price)
                    print('BUY:', destination_df['timestamp'].iloc[-1], 'price:', current_price, self.positions)
            elif signal == 'CLOSE':
                if self.position is not None or len(self.positions) > 0:
                    for position_price in self.positions:
                        profit = current_price - position_price
                        self.total_profit += profit
                    self.positions = []
                    print('CLOSE:', destination_df['timestamp'].iloc[-1], 'price:', current_price, 'total profit:', self.total_profit)
        except:
            pass

    '''
    static backtest is for existing static dataframe only, for live data will use live backtest  
    '''

    def apply_strategy_old(self, destination_df):
        try:
            signal = self.obj.run(destination_df)
            if signal in {'BUY__', 'CLOSE'}:
                print(signal, destination_df['timestamp'].iloc[-1], 'price:', destination_df['close'].iloc[-1])
        except:
            pass

    def run_static_simulation(self, n):
        n = n  # the number of runs
        if self.montecarlo: self.obj.set_random_vals()
        try:
            """backtest itself"""
            self.obj.run_test()
            """
            '''reporting'''
            run_params = vars(self.obj)
            run_params.pop('dataframe')
            #print(run_params)
            """
        except:
            pass

    """iterate thru dataframe and add the last row of initial dataframe to a new one
    while applying all the indicators and identifying entry points"""

    def run_live_simulation(self, n=None):
        n = self.num_runs  # the number of runs
        source_df = self.obj.obj.broker.dataframe
        destination_df = pd.DataFrame(columns=source_df.columns)
        max_rows = 50
        if self.montecarlo:
            self.obj.set_random_vals()
        # loop through each row in the source DataFrame and transfer it to the destination DataFrame
        for i, row in source_df.iterrows():
            # append the row to the destination DataFrame
            destination_df = pd.concat([destination_df, row.to_frame().T], ignore_index=True)
            # check if the number of rows in destination_df exceeds max_rows
            if len(destination_df) > max_rows:
                # drop the oldest row
                destination_df = destination_df.iloc[1:]
            # apply strategy to see if there is a signal
            self.apply_strategy(destination_df)
        print('profit:', self.total_profit)
        return -self.total_profit

    def run_backtest(self, method=None):
        if method not in ['static_simulation', 'live_simulation']:
            raise ValueError("Invalid method specified. Use 'static_simulation' or 'live_simulation'.")
        with Pool(5) as pool:
            getattr(self, method)(pool, range(self.num_runs))

    def static_simulation(self, pool, runs):
        pool.map(self.run_static_simulation, runs)

    def live_simulation(self, pool, runs):
        pool.map(self.run_live_simulation, runs)


''' obj - is DataStream object (eth, shib, etc.)'''


def test_strategy(obj, simulation_type='live', strategy=ChannelSlope):
    # Pass the DataStream obj to the strategy class
    apply_strategy = strategy(obj)
    #apply_strategy.set_custom_vals()
    opt = [32, -23, 0.76, 0.62, 23, 21, 29]
    apply_strategy.set_custom_vals_opt(opt)


    # Pass strategy to backtest
    apply_backtest = Backtest(apply_strategy)
    apply_backtest.montecarlo = False
    apply_backtest.num_runs = 1

    # Run the backtest with the appropriate method
    apply_backtest.run_backtest(f"{simulation_type}_simulation")


if __name__ == '__main__':

    SYMBOL = 'LTCUSDT'
    LIMIT = '150'
    TIMEFRAME = '5m'

    eth_test = TradingBot(SYMBOL, TIMEFRAME, LIMIT)
    test_strategy(eth_test, 'live')
