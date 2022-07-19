import json
import time
import copy
import pandas as pd
import requests
import websocket
import threading

from strategies.channel_slope import channel_slope
from backtest.backtest import




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


# process websocket data and append it to the initial-data dataframe
def on_message(ws, message):
    global current_df
    j = json.loads(message)['k']
    if j['x']:
        temp_df = pd.DataFrame([[j['T'], j['o'], j['h'], j['l'], j['c'], j['v']]],
                               columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        temp_df['timestamp'] = pd.to_datetime(j['T'] // 1000, unit='s')
        temp_df['open'] = temp_df['open'].astype(float)
        temp_df['high'] = temp_df['high'].astype(float)
        temp_df['low'] = temp_df['low'].astype(float)
        temp_df['close'] = temp_df['close'].astype(float)
        temp_df['volume'] = temp_df['volume'].astype(float)
        current_df.drop(index=current_df.index[0],
                        axis=0,
                        inplace=True)
        current_df = pd.concat([current_df, temp_df], sort=False, ignore_index=True)
        current_df.reset_index(drop=True)


def on_close(ws):
    print('### closed ###')


# receive real-time updates from websocket
def receive_stream_data(symbol, timeframe):
    socket = f'wss://stream.binance.us:9443/ws/{symbol}@kline_{timeframe}'
    ws = websocket.WebSocketApp(socket, on_message=on_message, on_close=on_close)
    ws.run_forever()


# process the (stream) data
# determine if we need to close or open a position
def process_data(current_df, deals_array):

    old_df = copy.copy(current_df)
    while True:
        if old_df.equals(current_df):
            '''compare the copy of the initial dataframe
            with the original to check if it got any updates '''
            time.sleep(10)
        else:
            ''' the updated dataframe is "old" now'''
            old_df = copy.copy(current_df)

            # all the indicators suppose to return signal and current or future price
            signal, price = channel_slope(old_df)

            check_if_close(deals_array, price)

            if signal:
                print(signal, price)
                # open_pos(signal, price)
                print('deals: ', deals_array.head())
            time.sleep(10)


def get_initial_klines(symbol, timeframe, limit=500):
    x = requests.get(f'https://api.binance.us/api/v3/klines?symbol={symbol}&limit={str(limit)}&interval={timeframe}')
    initial_data = pd.DataFrame(x.json())
    initial_data.drop([6, 7, 8, 9, 10, 11], axis=1, inplace=True)
    initial_data.rename(columns={0: 'timestamp',
                                 1: 'open',
                                 2: 'high',
                                 3: 'low',
                                 4: 'close',
                                 5: 'volume'}, inplace=True)
    initial_data['timestamp'] = pd.to_datetime(initial_data['timestamp'] // 1000, unit='s')
    initial_data['open'] = initial_data['open'].astype(float)
    initial_data['high'] = initial_data['high'].astype(float)
    initial_data['low'] = initial_data['low'].astype(float)
    initial_data['close'] = initial_data['close'].astype(float)
    initial_data['volume'] = initial_data['volume'].astype(float)
    return initial_data


if __name__ == "__main__":
    global df
    global profit_stop
    global deals_array
    '''[X, Y], where X is percent of price to calculate stop/profit
    and Y is percent of lot to close position i.e. [2,10] - 2% of price and 20% of lot left(!)
    last Y always should be 100 - since we want to close 100% of the lot '''
    profit_stop = {'take_profit': [[2, 20], [3, 20], [4, 20], [5, 20], [6, 100]],
                   'stop_loss': [[1, 50], [2, 100], ]}  # <====try to optimize
    deals_array = pd.DataFrame(columns=
                               ['pos_id', 'pos_type', 'open_price', 'volume',
                                'volume_left', 'profit_grid', 'stop_grid', 'status', 'profit'])
    # api_key = "ThZW140lmXAIen9huJ4ycQ0JzA5dQnofoQ6eP06BsuWZSU8lnohN9IofMjnYMRXW"
    # secret_key = "MpUPVpfELbhm86qc0qPDrf8LNKEYGmZfpnsWA7HQHdiu7fK3UY50rcgXrCvMh2lx"
    api_url = 'https://api.binance.us'
    SYMBOL = 'ETHUSDT'
    LIMIT = 100
    TIMEFRAME = '5m'

    current_df = get_initial_klines(SYMBOL, TIMEFRAME, LIMIT)

    t = threading.Thread(name='receive_stream_data', target=receive_stream_data, args=(SYMBOL.lower(), TIMEFRAME,))
    w = threading.Thread(name='process_data', target=process_data)

    w.start()
    t.start()

    w.join()
    t.join()
