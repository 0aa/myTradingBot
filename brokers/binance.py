import hashlib
import hmac
import json
import time
import urllib
import requests
import pandas as pd
import websocket

import config


class Binance:
    def __init__(self, symbol, timeframe, limit):
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = str(limit)
        self.__api_key = config.BINANCE_API_KEY
        self.__api_sec = config.BINANCE_API_SECRET_KEY
        self.api_url = 'https://api.binance.us'
        self.dataframe = self.get_initial_klines()

    def get_initial_klines(self):
        x = requests.get(
            f'{self.api_url}/api/v3/klines?symbol={self.symbol}&limit={self.limit}&interval={self.timeframe}')
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

    # process websocket data and append it to the end of initial-data dataframe
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
        print('### Connection closed ###')

    # receive real-time updates from websocket
    def receive_stream_data(self):
        socket = f'wss://stream.binance.us:9443/ws/{self.symbol.lower()}@kline_{self.timeframe}'
        ws = websocket.WebSocketApp(socket, on_message=self.on_message, on_close=self.on_close)
        ws.run_forever()

    def start(self):
        self.receive_stream_data()

    # get binance.us signature
    def get_binance_signature(self, data, secret):
        postdata = urllib.parse.urlencode(data)
        message = postdata.encode()
        byte_key = bytes(secret, 'UTF-8')
        mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
        return mac

    # Attaches auth headers and returns results of a POST request
    def binance_request(self, data, uri_path):
        headers = {'X-MBX-APIKEY': self.__api_key}
        signature = self.get_binance_signature(data, self.__api_sec)
        payload = {
            **data,
            "signature": signature,
        }
        req = requests.post((self.api_url + uri_path), headers=headers, data=payload)
        return req.text

    def get_all_open_orders(self):
        uri_path = '/api/v3/openOrders'
        data = {
            "timestamp": int(round(time.time() * 1000))
        }
        return self.binance_request(data, uri_path)

    """
    Order type (e.g., LIMIT, MARKET, STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT, LIMIT_MAKER)
    Order side (e.g., BUY, SELL)
    """

    def get_all_orders(self):
        uri_path = "/api/v3/allOrders"
        data = {
            "timestamp": int(round(time.time() * 1000)),
            "symbol": self.symbol
        }
        return self.binance_request(data, uri_path)

    def new_order(self, side, type, quantity):
        uri_path = "/api/v3/order"
        data = {
            "symbol": self.symbol,
            "side": side,
            "type": type,
            "quantity": quantity,
            "timestamp": int(round(time.time() * 1000))
        }
        return self.binance_request(data, uri_path)

    def test_new_order(self, side, type, quantity):
        uri_path = "/api/v3/order/test"
        data = {
            "symbol": self.symbol,
            "side": side,
            "type": type,
            "quantity": quantity,
            "timestamp": int(round(time.time() * 1000))
        }
        return self.binance_request(data, uri_path)


"""
SYMBOL = 'ETHUSDT'
LIMIT = '100'
TIMEFRAME = '5m'
eth = Binance(SYMBOL, TIMEFRAME, LIMIT)
result = eth.test_new_order('SELL', 'MARKET', 0.01)
#result = eth.get_all_open_orders()
print(result)

"""