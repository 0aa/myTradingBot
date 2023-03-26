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
        self.initial_message()

    def start_stream(self):
        self.broker.start_stream()

    def initial_message(self):
        text = (f"Type: TEST"
                f"\nSymbol: {self.broker.symbol}"
                f"\nTimeframe: {self.broker.timeframe}"
                f"\nTime: {time.strftime('%H:%M:%S', time.localtime())}")
        self.tg_bot.send_message(text)

# process the (stream) data
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

            if signal in ['CLOSE', 'BUY__']:
                text = (f"Signal: {signal}"
                        f"\nPrice: {old_df['close'].iloc[-1]}"
                        f"\nTime: {old_df['timestamp'].iloc[-1]}")
                obj.tg_bot.send_message(text)

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
