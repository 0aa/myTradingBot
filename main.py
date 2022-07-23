import json
import time
import copy
import pandas as pd
import requests
import websocket
import threading

from strategies.channel_slope import channel_slope
from helpers.helpers import close_if_below, close_if_above


class DataStream:

    def __init__(self, symbol, timeframe, limit):
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = str(limit)
        self.dataframe = self.get_initial_klines()
        self.profit_stop = {}
        self.deals_array = pd.DataFrame(columns=
                                        ['pos_id', 'pos_type', 'open_price', 'volume',
                                         'volume_left', 'profit_grid', 'stop_grid', 'status', 'profit'])

    def get_initial_klines(self):
        x = requests.get(
            f'https://api.binance.us/api/v3/klines?symbol={self.symbol}&limit={self.limit}&interval={self.timeframe}')
        self.dataframe = pd.DataFrame(x.json())
        self.dataframe.drop([6, 7, 8, 9, 10, 11], axis=1, inplace=True)
        self.dataframe.rename(columns={0: 'timestamp',
                                       1: 'open',
                                       2: 'high',
                                       3: 'low',
                                       4: 'close',
                                       5: 'volume'}, inplace=True)
        self.dataframe['timestamp'] = pd.to_datetime(self.dataframe['timestamp'] // 1000, unit='s')
        self.dataframe = self.dataframe.astype({'open': 'float64',
                                                'high': 'float64',
                                                'low': 'float64',
                                                'close': 'float64',
                                                'volume': 'float64'})
        return self.dataframe

    # process websocket data and append it to the initial-data dataframe
    def on_message(self, ws, message):
        j = json.loads(message)['k']
        if j['x']:
            temp_df = pd.DataFrame([[j['T'], j['o'], j['h'], j['l'], j['c'], j['v']]],
                                   columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            temp_df['timestamp'] = pd.to_datetime(j['T'] // 1000, unit='s')
            temp_df = temp_df.astype({'open': 'float64',
                                      'high': 'float64',
                                      'low': 'float64',
                                      'close': 'float64',
                                      'volume': 'float64'})
            self.dataframe.drop(index=self.dataframe.index[0],
                                axis=0,
                                inplace=True)
            self.dataframe = pd.concat([self.dataframe, temp_df], sort=False, ignore_index=True)
            self.dataframe.reset_index(drop=True)

    @staticmethod
    def on_close(ws):
        print('### closed ###')

    # receive real-time updates from websocket
    def receive_stream_data(self):
        socket = f'wss://stream.binance.us:9443/ws/{self.symbol.lower()}@kline_{self.timeframe}'
        ws = websocket.WebSocketApp(socket, on_message=self.on_message, on_close=self.on_close)
        ws.run_forever()

    def start(self):
        self.receive_stream_data()


# check if we need to close existing position at the current price
# df - dataFrame with existing positions
def check_if_close(temp_df, price):
    open_poses = temp_df.index[temp_df['status'] == 'open'].tolist()
    # pass grid type
    for i in open_poses:
        pos_type = temp_df.loc[i]['pos_type']
        match pos_type:
            case 'long':
                close_if_below('stop_grid', price, i)
                close_if_above('profit_grid', price, i)
            case 'short':
                close_if_below('profit_grid', price, i)
                close_if_above('stop_grid', price, i)


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
            signal, price = channel_slope(old_df)
            check_if_close(obj.deals_array, price)

            if signal:
                print(signal, price)
                # open_pos(signal, price)
                print('deals: ', obj.deals_array.head())

            time.sleep(10)


def test_strategy():
    pass


if __name__ == "__main__":
    '''[X, Y], where X is percent of price to calculate stop/profit
    and Y is percent of lot to close position i.e. [2,10] - 2% of price and 20% of lot left(!)
    last Y always should be 100 - since we want to close 100% of the lot '''
    profit_stop = {'take_profit': [[2, 20], [3, 20], [4, 20], [5, 20], [6, 100]],
                   'stop_loss': [[1, 50], [2, 100], ]}  # <====try to optimize
    # api_key = ""
    # secret_key = ""
    # api_url = 'https://api.binance.us'
    SYMBOL = 'ETHUSDT'
    LIMIT = '1000'
    TIMEFRAME = '5m'

    # create class object with the data we need
    eth = DataStream(SYMBOL, TIMEFRAME, LIMIT)
    eth.profit_stop = profit_stop

    t = threading.Thread(name='receive_stream_data', target=eth.start)
    w = threading.Thread(name='process_data', target=process_data, args=(eth,))

    w.start()
    t.start()

    w.join()
    t.join()
