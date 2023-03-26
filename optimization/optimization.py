import numpy as np
from scipy.optimize import minimize

from backtest.backtest import Backtest
from main import TradingBot
from strategies.channel_slope import ChannelSlope

# Set the initial guess for the minimum value of x


SYMBOL = 'ETHUSDT'
LIMIT = '150'
TIMEFRAME = '15m'
obj = TradingBot(SYMBOL, TIMEFRAME, LIMIT)
apply_strategy = ChannelSlope(obj)  # pass the DataStream obj to the strategy class


def minimize_params(params):
    print(params)
    apply_strategy.set_custom_vals_opt(params)
    apply_backtest = Backtest(apply_strategy)  # pass strategy to backtest
    return apply_backtest.run_live_simulation()


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
    # res=minimize_params(x0)
    # Call the minimize function
    x0 = np.array([32, -23, 0.76, 0.62, 23, 21, 29], dtype=float)
    bounds = ((-100, 100), (-100, 100), (0, 1), (0, 1), (2, 30), (2, 30), (2, 30))

    res = minimize(minimize_params, x0, method='Powell', bounds=bounds,
                   options={'disp': True, 'ftol': 1, 'xtol': 1, 'maxiter': 1000})

    # Print the result
    print(res)
