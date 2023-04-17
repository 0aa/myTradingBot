import time

from copy import deepcopy
from threading import Thread

from brokers.binance import Binance
from playground.positionManagement import PositionManagement
from utils.csvUtil import Trades
from strategies.channelSlope import ChannelSlope


class TradingBot:
    def __init__(self, symbol, timeframe, limit, start_time=None, end_time=None):
        self.broker = Binance(symbol, timeframe, limit, start_time, end_time)
        self.trades = Trades(symbol, timeframe, limit)
        self.default_strategy = ChannelSlope
        self.strategy = self.set_strategy(self.default_strategy)
        self.PM = PositionManagement(self.strategy)
        self.PM.rg_switch = True

        self.tg_bot = self.PM.tg_bot

    def start_stream(self):
        self.broker.start_stream()

    def initial_message(self, run_type):
        text = (f"Type: {run_type}"
                f"\nSymbol: {self.broker.symbol}"
                f"\nTimeframe: {self.broker.timeframe}"
                f"\nTime: {time.strftime('%H:%M:%S', time.localtime())}")
        self.tg_bot.send_message(text)

    def set_strategy(self, strategy):
        return strategy(self.broker)

    def run_bot_test(self):
        self.initial_message("TEST RUN")
        old_dataframe = deepcopy(self.broker.dataframe)
        while True:
            if old_dataframe.equals(self.broker.dataframe):
                time.sleep(10)
            else:
                old_dataframe = deepcopy(self.broker.dataframe)
                signal = self.PM.apply_strategy(old_dataframe)
                if signal:
                    try:
                        result = self.broker.open_position_test(signal)
                        self.tg_bot.send_message(f"Test Position: {result}")
                    except Exception as e:
                        print(f"Error while opening position: {e}")
                        self.tg_bot.send_message(f"Error while opening position: {e}")
                time.sleep(50)

    def run_bot_prod(self):
        self.initial_message("PROD RUN")
        old_dataframe = deepcopy(self.broker.dataframe)
        while True:
            if old_dataframe.equals(self.broker.dataframe):
                time.sleep(10)
            else:
                old_dataframe = deepcopy(self.broker.dataframe)
                signal = self.PM.apply_strategy(old_dataframe)
                if signal:
                    try:
                        result = self.broker.open_position(signal)
                        self.tg_bot.send_message(f"Position posted: {result}")
                    except Exception as e:
                        print(f"Error while opening position: {e}")
                        self.tg_bot.send_message(f"Error while opening position: {e}")

                time.sleep(50)

def main():
    """config file needs to be created with the api keys/tokens"""
    SYMBOL = 'ETHUSDT'
    TIMEFRAME = '1m'
    LIMIT = '100'  # number of beginning candles
    # START_DATE = '2023-4-1'   # time format 'YYYY-M-D'
    # END_DATE = '2023-4-15'    # optional

    # use following sequence: SYMBOL, TIMEFRAME, LIMIT, START_DATE, END_DATE
    eth = TradingBot(SYMBOL, TIMEFRAME, LIMIT)

    t = Thread(name='receive stream', target=eth.start_stream)
    w = Thread(name='run the bot', target=eth.run_bot_test)
    #  w = Thread(name='run the bot', target=eth.run_bot_test, args=(eth,))
    t.start()
    w.start()

    t.join()
    w.join()


"""start point"""
if __name__ == "__main__":
    main()
