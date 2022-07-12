import json
import time
import copy
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
import websocket
from multiprocessing import Process, Queue
import threading


# To find a slope of price line
def indSlope(series, n):
    array_sl = [j * 0 for j in range(n - 1)]
    for j in range(n, len(series) + 1):
        y = series[j - n:j]
        x = np.array(range(n))
        x_sc = (x - x.min()) / (x.max() - x.min())
        y_sc = (y - y.min()) / (y.max() - y.min())
        x_sc = sm.add_constant(x_sc)
        model = sm.OLS(y_sc, x_sc)
        results = model.fit()
        array_sl.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(array_sl))))
    return np.array(slope_angle)


# find local mimimum / local maximum
def isLCC(DF, i):
    df = DF.copy()
    LCC = 0

    if df['close'][i] <= df['close'][i + 1] and df['close'][i] <= df['close'][i - 1] < df['close'][i + 1]:
        # найдено Дно
        LCC = i - 1
    return LCC


def isHCC(DF, i):
    df = DF.copy()
    HCC = 0
    if df['close'][i] >= df['close'][i + 1] and df['close'][i] >= df['close'][i - 1] > df['close'][i + 1]:
        # найдена вершина
        HCC = i
    return HCC


def getMaxMinChannel(DF, n):
    maxx = 0
    minn = DF['low'].max()
    for i in range(1, n):
        if maxx < DF['high'][len(DF) - i]:
            maxx = DF['high'][len(DF) - i]
        if minn > DF['low'][len(DF) - i]:
            minn = DF['low'][len(DF) - i]
    return maxx, minn


# True Range and Average True Range indicator
def indATR(source_DF, n):
    df = source_DF.copy()
    df['H-L'] = abs(df['high'] - df['low'])
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df_temp = df.drop(['H-L', 'H-PC', 'L-PC'], axis=1)
    return df_temp


# generate data frame with all needed data
# this is just one specific strategy func
def PrepareDF(DF):
    ohlc = DF.iloc[:, [0, 1, 2, 3, 4, 5]]
    ohlc.columns = ["date", "open", "high", "low", "close", "volume"]
    ohlc = ohlc.set_index('date')
    df = indATR(ohlc, 14).reset_index()
    df['slope'] = indSlope(df['close'], 5)
    df['channel_max'] = df['high'].rolling(10).max()
    df['channel_min'] = df['low'].rolling(10).min()
    df['position_in_channel'] = (df['close'] - df['channel_min']) / (df['channel_max'] - df['channel_min'])
    df = df.set_index('date')
    df = df.reset_index()
    return df


def raw_data(path):
    return pd.read_csv(path)


# process websocket data and append it to the initial-data dataframe
def on_message(ws, message):
    global df
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
        df.drop(index=df.index[0],
                axis=0,
                inplace=True)
        df = pd.concat([df, temp_df], sort=False, ignore_index=True)
        df.reset_index(drop=True)


def on_close(ws):
    print('### closed ###')


# receive real-time updates from websocket
def receive_stream_data(symbol, timeframe):
    socket = f'wss://stream.binance.us:9443/ws/{symbol}@kline_{timeframe}'
    ws = websocket.WebSocketApp(socket, on_message=on_message, on_close=on_close)
    ws.run_forever()


# process the (stream) data
# determine if we need to close or open a position
def process_data():
    global df
    global deals_array
    old_df = copy.copy(df)
    while True:
        if old_df.equals(df):
            '''compare the copy of the initial dataframe
            with the original to check if it got any updates '''
            time.sleep(10)
        else:
            ''' the updated dataframe is "old" now'''
            old_df = copy.copy(df)

            # strategy specific
            prepared_df = PrepareDF(df)

            signal, price = check_if_signal(prepared_df)
            check_if_close(deals_array, price)

            if signal:
                print(signal, price)
                open_pos(signal, price)
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

    df = get_initial_klines(SYMBOL, TIMEFRAME, LIMIT)

    t = threading.Thread(name='receive_stream_data', target=receive_stream_data, args=(SYMBOL.lower(), TIMEFRAME,))
    w = threading.Thread(name='process_data', target=process_data)

    w.start()
    t.start()

    w.join()
    t.join()
