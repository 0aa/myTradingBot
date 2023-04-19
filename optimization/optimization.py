import threading
from datetime import datetime
from queue import Queue

import mplfinance as mpf

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.optimize import minimize, Bounds
from multiprocessing import Pool
from backtest.backtest import Backtest
from brokers.binance import Binance
from strategies.channelSlope import ChannelSlope


class Optimization:

    def __init__(self, strategy):
        self.strategy = strategy
        self.backtest = Backtest(strategy)
        self.dataframe = strategy.dataframe
        self.optimization_result = pd.DataFrame()

        self.bounds = None

        self.pool_size = 5
        self.num_runs = 20

    def montecarlo_pool(self, method='pool_live_simulation'):
        if method not in ['pool_static_simulation', 'pool_live_simulation']:
            raise ValueError("Invalid method specified. Use 'static_simulation' or 'live_simulation'.")
        elif method == 'pool_static_simulation':
            self.pool_static_simulation()
        elif method == 'pool_live_simulation':
            self.pool_live_simulation()

    def pool_live_simulation(self):
        with Pool(processes=self.pool_size) as pool:
            results = pool.map(self.run_montecarlo_backtest, range(self.num_runs))
            self.optimization_result = pd.concat(results).reset_index(drop=True)

    def pool_static_simulation(self):
        with Pool(processes=self.pool_size) as pool:
            pass

    def montecarlo_thread(self, method='thread_live_simulation'):
        if method not in ['thread_static_simulation', 'thread_live_simulation']:
            raise ValueError("Invalid method specified. Use 'static_simulation' or 'live_simulation'.")
        elif method == 'thread_static_simulation':
            pass
        elif method == 'thread_live_simulation':
            self.thread_live_simulation()

    def thread_live_simulation(self):
        def worker():
            while not task_queue.empty():
                task_index = task_queue.get()
                result = self.run_montecarlo_backtest(task_index)
                results_queue.put(result)
                task_queue.task_done()

        task_queue = Queue()
        results_queue = Queue()

        for i in range(self.num_runs):
            task_queue.put(i)

        threads = []
        for _ in range(self.pool_size):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        self.optimization_result = pd.concat(results).reset_index(drop=True)

    def run_montecarlo_backtest(self, n=None):
        # create new instance of the backtest class
        montecarlo_backtest = Backtest(self.strategy)

        # set random values for the backtest and strategy
        params_strategy = self.set_random_ChannelSlope_values(self.strategy)
        params_backtest = self.set_random_backtest_values(montecarlo_backtest)

        profit_loss = montecarlo_backtest.run_live_simulation()
        analytics_df = montecarlo_backtest.statistics_dataframe

        run_results = pd.DataFrame(
            {'Profit': [round(profit_loss, 2)], 'Trades': [len(analytics_df)],
             'Backtest Params': [params_backtest], 'Strategy Params': [params_strategy]})
        result = pd.concat([self.optimization_result, run_results], ignore_index=True)
        return result

    def set_random_ChannelSlope_values(self, strategy):
        """ default params = [5, 5, 0.5, 0.5, 14, 10, 5] """

        p1 = np.random.uniform(-80, -10)  # close_slope
        p2 = 22  # np.random.uniform(-10, 30)  # long_slope
        p3 = 0.35  # np.random.uniform(0.01, 0.70)  # close_pos_in_channel
        p4 = 0.32  # np.random.uniform(0.15, 0.80)  # long_pos_in_channel
        p5 = 0  # int(np.random.uniform(2, 30))  # rsi_period
        p6 = 6  # int(np.random.uniform(2, 30))  # maxmin_period
        p7 = 10  # int(np.random.uniform(4, 30))  # slope_period
        params = [p1, p2, p3, p4, p5, p6, p7]

        # params = [-30, 3.7, 0.17, 0.44, 7, 6, 18]

        strategy.set_custom_vals_opt(params)
        return params

    def set_random_backtest_values(self, montecarlo_backtest):
        p1 = 15000   # max_amount
        p2 = 3  # (np.random.uniform(1, 10))  # max_positions
        p3 = 0.985 # round(np.random.uniform(0.9, 0.999), 3)  # stop_loss
        p4 = 1.1  # round(np.random.uniform(1.001, 1.100), 3)  # take_profit
        p5 = 5  # round(np.random.uniform(0.1, 5), 2)  # lot_one
        p6 = 1  # round(np.random.uniform(0.1, 5), 2)  # lot_two
        p7 = 1  # round(np.random.uniform(0.1, 5), 2)  # lot_three
        params = [p1, p2, p3, p4, p5, p6, p7]

        ##params = [15000, 3, 0.985, 1.01, 5, 1, 1]

        montecarlo_backtest.set_custom_params(params)
        return params

    def print_results(self):
        self.optimization_result = self.optimization_result.sort_values('Profit', ascending=False)
        print(self.optimization_result.to_string())

    def build_plot(self):
        # Convert the index to a DatetimeIndex
        self.dataframe = self.dataframe.set_index('Timestamp')
        # self.dataframe.index = pd.to_datetime(self.dataframe.index)

        # Plot the stock price chart
        mpf.plot(self.dataframe, type='candle', style='charles',
                 title=f'Stock Price',
                 ylabel='Price',
                 ylabel_lower='Volume',
                 volume=True,
                 figsize=(14, 7))


def int_objective_function(params):
    integer_params = [round(num) for num in params]
    return integer_params


def minimize_params(params):
    params = int_objective_function(params)
    strategy.set_custom_vals_ind(params)
    apply_backtest = Backtest(strategy)  # pass strategy to backtest
    result = apply_backtest.run_live_simulation()
    print(f"Inverted profit: {result}, params: {params}")
    return -result


if __name__ == '__main__':
    # res=minimize_params(x0)
    # Call the minimize function
    start_time = datetime.now()

    SYMBOL = 'ETHUSDT'
    LIMIT = '1000'
    TIMEFRAME = '1h'
    # time YYYY,M,D
    START_TIME = '2023-4-1'
    END_TIME = '2023-4-15'  # optional
    # create class object with the data we need

    # create the dataframe
    eth_test = Binance(SYMBOL, TIMEFRAME, LIMIT, START_TIME, END_TIME)
    # create strategy class
    strategy = ChannelSlope(eth_test)  # pass the DataStream obj to the strategy class

    optimize = Optimization(strategy)
    # optimize.build_plot()
    optimize.montecarlo_pool()
    # optimize.montecarlo_thread()
    optimize.print_results()

    end_time = datetime.now()
    print("Execution time:", end_time - start_time, "seconds")

    # x0 = np.array([8, 15, 8], dtype=int)
    # bounds = [(1, 30), (1, 30), (1, 20)]
    # res = minimize(minimize_params, x0, method='Powell', bounds=bounds)
    # Print the result
    # print(res)
    """
    x0 = np.array([36, -36, 0.76, 0.62], dtype=float)
    bounds = ((0, 100), (-100, 0), (0, 1), (0, 1))


    res = minimize(minimize_params, x0, method='Powell', bounds=bounds,
                   options={'disp': True, 'ftol': 1, 'xtol': 1, 'maxiter': 1000})

    # Print the result
    print(res)

    
    exchange_id = 'binanceus'  # Choose the exchange (e.g., Binance)
    symbol = 'ETH/USDT'  # Choose the trading pair (e.g., Bitcoin to Tether)
    timeframe = '30m'  # Choose the timeframe (e.g., daily data)

    historical_data = fetch_historical_data(exchange_id, symbol, timeframe)
    #print(historical_data.to_string())
    a = ChannelSlope()
    b = a.run(historical_data)
    print(b)
    
    
    
    
    symbol = 'AAPL'  # Apple Inc.
start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.datetime(2022, 1, 1)

# Fetch stock price data using pandas_datareader
stock_data = web.DataReader(symbol, 'yahoo', start_date, end_date)
    """
