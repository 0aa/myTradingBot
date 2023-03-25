import time
import copy
import threading

from brokers.binance import Binance
from utils.csv_util import Trades
from utils.telegram_bot import TelegramBot
from strategies.channel_slope import ChannelSlope


class TradingBot:
    def __init__(self, symbol, timeframe, limit):
        self.broker = Binance(symbol, timeframe, limit)
        # self.dataframe = self.broker.dataframe
        self.trades = Trades(symbol, timeframe, limit)
        self.tg_bot = TelegramBot()

    def start_stream(self):
        self.broker.start_stream()


# process the (stream) data
# determine if we need to close or open a position
def run_trading_bot(obj):
    old_df = copy.copy(obj.broker.dataframe)
    strategy = ChannelSlope(obj)
    while True:
        if old_df.equals(obj.broker.dataframe):
            '''compare the copy of the initial dataframe
            with the original to check if it got any updates '''
            time.sleep(1)
        else:
            ''' the updated dataframe is "old" now'''
            old_df = copy.copy(obj.broker.dataframe)
            # all the indicators suppose to return signal and current or future price
            signal = strategy.run()
            print('signal', signal)

            time.sleep(50)


"""start point"""
if __name__ == "__main__":
    """config file needs to be created with the api keys/tokens"""
    SYMBOL = 'ETHUSDT'
    LIMIT = '50'
    TIMEFRAME = '1m'

    # create class object with the data we need
    eth = TradingBot(SYMBOL, TIMEFRAME, LIMIT)

    t = threading.Thread(name='receive stream', target=eth.start_stream)
    w = threading.Thread(name='run the bot', target=run_trading_bot, args=(eth,))

    t.start()
    w.start()

    t.join()
    w.join()
