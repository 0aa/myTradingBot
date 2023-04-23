import time

from copy import deepcopy
from threading import Thread

from brokers.binance import Binance
from utils.positionManagement import PositionManagement
from utils.csvUtil import Trades
from strategies.channelSlope import ChannelSlope


class TradingBot:
    def __init__(self, symbol, timeframe, limit, start_time=None, end_time=None):
        self.broker = Binance(symbol, timeframe, limit, start_time, end_time)
        self.trades = Trades(symbol, timeframe, limit)
        self.default_strategy = ChannelSlope
        self.strategy = self.set_strategy(self.default_strategy)
        self.PM = PositionManagement(self.strategy)
        self.PM.tg_switch = True

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



    def run_bot(self, env):

        self.initial_message(f"{env} RUN")
        old_dataframe = deepcopy(self.broker.dataframe)
        stop_loss_ids = []

        def handle_buy(payload):
            if env == "TEST":
                return self.broker.open_position_test(payload)
            elif env == "PROD":
                return self.broker.open_position(payload)

        def handle_sell(payload):
            if len(stop_loss_ids) > 0:
                for order_id in stop_loss_ids:
                    if env == "TEST":
                        self.broker.delete_existing_order_test(order_id)
                    elif env == "PROD":
                        self.broker.delete_existing_order(order_id)
                    stop_loss_ids.remove(order_id)

            if env == "TEST":
                return self.broker.open_position_test(payload)
            elif env == "PROD":
                return self.broker.open_position(payload)

        def handle_stop_loss(payload):
            if env == "TEST":
                result = self.broker.open_position_test(payload)
                stop_loss_ids.append({'orderId': 123456789})
            elif env == "PROD":
                result = self.broker.open_position(payload)
                stop_loss_ids.append({'orderId': result['orderId']})
            return result


        while True:
            if old_dataframe.equals(self.broker.dataframe):
                time.sleep(10)
            else:
                old_dataframe = deepcopy(self.broker.dataframe)
                payloads = self.PM.apply_strategy(old_dataframe)

                if payloads:
                    try:
                        for payload in payloads:
                            print(f"{env} Payload: {payload}, {time.ctime()}")

                            if payload['side'] == 'BUY' and payload['type'] == 'MARKET':
                                result = handle_buy(payload)
                            elif payload['side'] == 'SELL' and payload['type'] == 'MARKET':
                                result = handle_sell(payload)
                            elif payload['side'] == 'SELL' and payload['type'] == 'STOP_LOSS_LIMIT':
                                result = handle_stop_loss(payload)

                            self.tg_bot.send_message(f"{env}: Position posted: {result}"
                                                     f"\nSide: {payload['side']}"
                                                     f"\nType: {payload['type']}"
                                                     f"\nTime: {time.ctime()}")
                            time.sleep(0.2)
                    except Exception as e:
                        print(f"{env}: Error while opening position: {e}")
                        self.tg_bot.send_message(f"{env}: Error while opening position: {e}")
                time.sleep(50)

    def run_bot_prod(self):
        self.run_bot("PROD")

    def run_bot_test(self):
        self.run_bot("TEST")


def main():
    """config file needs to be created with the api keys/tokens"""
    SYMBOL = 'ETHUSD'
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
