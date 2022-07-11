import json
import time

import numpy as np
import pandas as pd
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


# generate data frame with all needed data
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
    return (df)


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
    return (df)


def raw_data(path):
    return pd.read_csv(path)


def stream_data(socket):
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(socket, on_message=onMessage, on_close=onClose)
    ws.run_forever()


def onMessage(ws, message):
    global df
    json_message = json.loads(message)['k']
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(json_message['T'] // 1000))
    openP = json_message['o']
    highP = json_message['h']
    lowP = json_message['l']
    closeP = json_message['c']
    volume = json_message['v']
    df2 = pd.DataFrame([[timestamp, openP, highP, lowP, closeP, volume]],
                       columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df = pd.concat([df, df2], sort=False, ignore_index=True)


def onClose(ws):
    print("#closed#")


def print_my():
    global df
    while True:
        print(df)
        time.sleep(4)


if __name__ == "__main__":
    API_KEY = 'HO0PUVKW0S8C5V0D'
    INTERVAL = '5min'
    SYMBOL = 'ETH'
    RAW_URL = f"https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol={SYMBOL}&market=USD&interval={INTERVAL}&apikey={API_KEY}&datatype=csv&outputsize=full"
    SOCKET = f"wss://stream.binance.com:9443/ws/{SYMBOL.lower()}usdt@kline_1m"

    df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df5 = raw_data(RAW_URL)
    df = df5.copy()[::-1]

    p0 = threading.Thread(target=stream_data, args=(SOCKET,))
    p1 = threading.Thread(target=print_my)
    p0.start()
    p1.start()
    p0.join()
    p1.join()
    print("Hello")

'''    
    p1 = Process(target=multi_threading, args=(deep, temp_proxy, url, title, headless))  # yt_search
    p1.start()
    p1.join()
'''
