import time
import copy
import threading

from brokers.binance import Binance
from strategies.channel_slope import ChannelSlope
from backtest.backtest import Backtest
from utils.csv_util import Trades
from utils.telegram_bot import TelegramBot


class TradingBot:
    def __init__(self, symbol, timeframe, limit):
        self.broker = Binance(symbol, timeframe, limit)
        self.dataframe = self.broker.dataframe
        self.trades = Trades(symbol, timeframe, limit)
        self.tg_bot = TelegramBot()


"""the following will be moved to TradeEngine() module"""


# check if we need to close existing position at the current price
# df - dataFrame with existing positions
def check_if_close(temp_df, price):
    open_poses = temp_df.index[temp_df['status'] == 'open'].tolist()
    # pass grid type
    for i in open_poses:
        pos_type = temp_df.loc[i]['pos_type']
        match pos_type:
            case 'long':
                pass
            case 'short':
                pass


# process the (stream) data
# determine if we need to close or open a position
def process_data(obj):
    old_df = copy.copy(obj.dataframe)
    while True:
        if old_df.equals(obj.dataframe):
            '''compare the copy of the initial dataframe
            with the original to check if it got any updates '''
            time.sleep(10)
        else:
            ''' the updated dataframe is "old" now'''
            old_df = copy.copy(obj.dataframe)
            # all the indicators suppose to return signal and current or future price
            signal, price = ChannelSlope.channel_slope(old_df)
            check_if_close(obj.deals_array, price)

            if signal:
                print(signal, price)
                # open_pos(signal, price)
                print('deals: ', obj.deals_array.head())

            time.sleep(10)


''' the following needs to be moved inside BackTest module
obj - is DataStream object (eth, shib, etc.)'''


def test_strategy(obj):
    # dataframe = obj.dataframe  # pull dataframe from the object
    apply_str = ChannelSlope(obj)  # pass the DataStream obj to the strategy class
    apply_str.set_default_vals()
    apply_bt = Backtest(apply_str)  # pass strategy to backtest
    apply_bt.montecarlo = False
    apply_bt.num_runs = 1
    apply_bt.run_pool()
    # start loop
    # exit from the loop
    # save results
    # optimize results


'''
SYMBOL = 'ETHUSDT'
LIMIT = '100'
TIMEFRAME = '5m'
obj = DataStream(SYMBOL, TIMEFRAME, LIMIT)
apply_str = ChannelSlope(obj)  # pass the DataStream obj to the strategy class
'''


def minimize_params(params):
    print(params)
    apply_str.set_custom_vals_opt(params)
    apply_bt = Backtest(apply_str)  # pass strategy to backtest
    return apply_bt.run_static_backtest()


"""start point"""
if __name__ == "__main__":

    """config file needs to be created with the api keys/tokens"""
    SYMBOL = 'ETHUSDT'
    LIMIT = '100'
    TIMEFRAME = '30m'

    # create class object with the data we need
    eth = TradingBot(SYMBOL, TIMEFRAME, LIMIT)

    # t = threading.Thread(name='receive_stream_data', target=eth.start)
    # w = threading.Thread(name='process data', target=process_data, args=(eth,))
    backtest = threading.Thread(name='test strategy', target=test_strategy, args=(eth,))

    # t.start()
    # w.start()
    backtest.start()

    # t.join()
    # w.join()
    backtest.join()
