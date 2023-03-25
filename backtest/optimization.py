import numpy as np
from scipy.optimize import minimize

from main import TradingBot
from strategies.channel_slope import ChannelSlope
from backtest.backtest import Backtest


# Define the function to be minimized
def rosen(x):
    return sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2)


# Set the initial guess for the minimum value of x
x0 = np.array([5, 5, 5, 5, 14, 10, 5])


SYMBOL = 'ETHUSDT'
LIMIT = '100'
TIMEFRAME = '5m'
obj = TradingBot(SYMBOL, TIMEFRAME, LIMIT)
apply_str = ChannelSlope(obj)  # pass the DataStream obj to the strategy class


def minimize_params(params):
    print(params)
    apply_str.set_custom_vals_opt(params)
    apply_bt = Backtest(apply_str)  # pass strategy to backtest
    return apply_bt.run_static_simulation()


# res=minimize_params(x0)
# Call the minimize function
bounds = ((-100, 100), (-100, 100), (1, 10), (1, 10), (2, 30), (2, 30), (2, 30))
res = minimize(minimize_params, x0, method='Powell', bounds=bounds, options={'disp': True})

# Print the result
print(res)
