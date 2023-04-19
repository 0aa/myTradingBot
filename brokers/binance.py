import requests
import hmac
import json
import pandas as pd

from time import time
from hashlib import sha256
from urllib import parse
from datetime import datetime, timedelta
from pytz import timezone
from websocket import WebSocketApp

import config


class Binance:
    def __init__(self, symbol, timeframe, limit, start_date=None, end_date=None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = str(limit)
        self.__api_key = config.BINANCE_API_KEY
        self.__api_sec = config.BINANCE_API_SECRET_KEY
        self.api_url = 'https://api.binance.us'
        self.params = {"symbol": symbol,
                       "limit": str(limit),
                       "interval": timeframe}
        self.dataframe = self.get_klines(start_date, end_date)

    original_timezone = timezone('UTC')
    target_timezone = timezone('US/Eastern')

    def get_klines(self, start_date, end_date):
        if start_date is None:
            data = self.get_initial_klines()
        elif end_date is None:
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp()) * 1000
            self.params['startTime'] = start_timestamp
            data = self.get_initial_klines()
        elif start_date is not None and end_date is not None:
            data = self.get_unlimited_klines(start_date, end_date)
        else:
            raise Exception(f'Start and/or End dates are incorrect: Start: {start_date}; End:{end_date}')
        return data

    def get_initial_klines(self):
        x = requests.get(f'{self.api_url}/api/v3/klines', params=self.params)
        dataframe = pd.DataFrame(x.json())
        dataframe.drop([6, 7, 8, 9, 10, 11], axis=1, inplace=True)
        dataframe.rename(columns={0: 'Timestamp',
                                  1: 'Open',
                                  2: 'High',
                                  3: 'Low',
                                  4: 'Close',
                                  5: 'Volume'}, inplace=True)
        dataframe['Timestamp'] = pd.to_datetime(dataframe['Timestamp'] // 1000, unit='s')
        # convert to Eastern Time
        dataframe['Timestamp'] = dataframe['Timestamp'].dt.tz_localize(
            self.original_timezone).dt.tz_convert(self.target_timezone)
        dataframe = dataframe.astype({'Open': 'float64',
                                      'High': 'float64',
                                      'Low': 'float64',
                                      'Close': 'float64',
                                      'Volume': 'float64'})
        return dataframe

    def get_multiple_dataframes(self, start_date, end_date):
        df_5m = self.get_unlimited_klines(start_date, end_date)
        df_5m['Timestamp'] = pd.to_datetime(df_5m['Timestamp'])
        df_5m = df_5m.set_index('Timestamp')
        df_30m = df_5m.resample('30min').agg(
            {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        df_5m = df_5m.reset_index()
        df_30m = df_30m.reset_index()
        return df_5m, df_30m

    def get_unlimited_klines(self, start_date, end_date):
        dataframe = pd.DataFrame()
        start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
        end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)

        interval_mapping = {
            '1m': timedelta(minutes=1),
            '3m': timedelta(minutes=3),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '30m': timedelta(minutes=30),
            '1h': timedelta(hours=1),
            '2h': timedelta(hours=2),
            '4h': timedelta(hours=4),
            '6h': timedelta(hours=6),
            '8h': timedelta(hours=8),
            '12h': timedelta(hours=12),
            '1d': timedelta(days=1),
            '3d': timedelta(days=3),
            '1w': timedelta(weeks=1),
            '1M': timedelta(days=30)
        }

        interval_delta = interval_mapping.get(self.params['interval'])

        while start_timestamp < end_timestamp:
            self.params['startTime'] = start_timestamp
            temp_dataframe = self.get_initial_klines()
            if temp_dataframe.empty:
                break

            last_timestamp = temp_dataframe.iloc[-1, 0]
            start_timestamp = int((last_timestamp.to_pydatetime() + interval_delta).timestamp() * 1000)

            dataframe = pd.concat([dataframe, temp_dataframe], ignore_index=True)

        return dataframe

    #  process websocket data and append it to the end of initial-data dataframe
    def on_message(self, ws, message):
        j = json.loads(message)['k']
        if j['x']:
            temp_df = pd.DataFrame([[j['T'], j['o'], j['h'], j['l'], j['c'], j['v']]],
                                   columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            temp_df['Timestamp'] = pd.to_datetime(j['T'] // 1000, unit='s')
            # convert Timestamp to Your Timezone
            temp_df['Timestamp'] = temp_df['Timestamp'].dt.tz_localize(
                self.original_timezone).dt.tz_convert(self.target_timezone)
            temp_df = temp_df.astype({'Open': 'float64',
                                      'High': 'float64',
                                      'Low': 'float64',
                                      'Close': 'float64',
                                      'Volume': 'float64'})
            self.dataframe.drop(index=self.dataframe.index[0], axis=0, inplace=True)
            self.dataframe = pd.concat([self.dataframe, temp_df], sort=False, ignore_index=True)
            self.dataframe.reset_index(drop=True)

    @staticmethod
    def on_close(ws):
        print('### Connection closed ###')

    # receive real-time updates from websocket
    def receive_stream_data(self):
        socket = f'wss://stream.binance.us:9443/ws/{self.symbol.lower()}@kline_{self.timeframe}'
        ws = WebSocketApp(socket, on_message=self.on_message, on_close=self.on_close)
        ws.run_forever()

    def start_stream(self):
        self.receive_stream_data()

    # get binance.us signature
    def get_binance_signature(self, data, secret):
        postdata = parse.urlencode(data)
        message = postdata.encode()
        byte_key = bytes(secret, 'UTF-8')
        mac = hmac.new(byte_key, message, sha256).hexdigest()
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
            "timestamp": int(round(time() * 1000))
        }
        return self.binance_request(data, uri_path)

    """
    Order type (e.g., LIMIT, MARKET, STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT, LIMIT_MAKER)
    Order side (e.g., BUY, SELL)
    """

    def get_all_orders(self):
        uri_path = "/api/v3/allOrders"
        data = {
            "timestamp": int(round(time() * 1000)),
            "symbol": self.symbol
        }
        return self.binance_request(data, uri_path)

    def open_position(self, param):
        """
        Create a new order on the Binance trading platform.

        Args:
            side (str): Order side, which can be 'BUY' or 'SELL'.
            type (str): Order type, which can be one of the following:
                        'LIMIT', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT', 'LIMIT_MAKER'.
            quantity (float): Quantity of the trading asset to buy or sell.

        Returns:
            dict: Response from the Binance API.

        Parameters:
            symbol (str): Order trading pair, e.g., 'BTCUSD', 'ETHUSD'.
            side (str): Order side, e.g., 'BUY', 'SELL'.
            type (str): Order type, e.g., 'LIMIT', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT', 'LIMIT_MAKER'.
            timeInForce (str, optional): Time in force for the order (e.g., 'GTC', 'IOC', 'FOK'). Not used in this implementation.
            quantity (float, optional): Quantity of the trading asset to buy or sell.
            quoteOrderQty (float, optional): Quote order quantity. Not used in this implementation.
            price (float, optional): Order price. Not used in this implementation.

        """
        uri_path = "/api/v3/order"
        data = {
            "symbol": self.symbol,
            "side": None,
            "type": None,
            "quantity": None,
            "timeInForce": "GTC",
            "timestamp": int(round(time() * 1000))
        }
        data |= param
        return self.binance_request(data, uri_path)

    def open_position_test(self, param):
        uri_path = "/api/v3/order/test"
        data = {
            "symbol": self.symbol,
            "side": None,
            "type": None,
            "quantity": None,
            "timeInForce": "GTC",
            "timestamp": int(round(time() * 1000))
        }
        data |= param
        response = self.binance_request(data, uri_path)
        if response == '{}':
            return "Test Position Posted"
        else:
            return response


"""
SYMBOL = 'ETHUSD'
LIMIT = '50'
TIMEFRAME = '5m'
START_TIME = '2023-4-16'
END_TIME = '2023-4-17'  # optional
eth = Binance(SYMBOL, TIMEFRAME, LIMIT)

current_price = 2079
stop_loss_price = current_price * 0.985
stop_loss_price_limit = current_price * 0.99
quantity = 0.001  # Adjust the quantity as needed

response = eth.open_position()
print(response)


df_5m, df_30m = eth.get_multiple_dataframes(START_TIME, END_TIME)
def get_five_min_slice(df_5m, df_30m):
    df_5m = df_5m.set_index('Timestamp')
    df_30m = df_30m.set_index('Timestamp')
    last_row_timestamp = df_30m.iloc[-1].name
    second_last_row_timestamp = df_30m.iloc[-2].name
    sliced_df = df_5m[(df_5m.index >= second_last_row_timestamp) & (df_5m.index <= last_row_timestamp)]
    sliced_df = sliced_df.iloc[1:-1]
    sliced_df = sliced_df.reset_index()
    return sliced_df


def get_corresponding_interval(df_5m, df_30m):
    source_df = df_30m
    destination_df = pd.DataFrame(columns=source_df.columns)
    max_rows = 30

    for i, row in source_df.iterrows():
        destination_df = pd.concat([destination_df, row.to_frame().T], ignore_index=False)
        if len(destination_df) > 1:
            slice = get_five_min_slice(df_5m, df_30m)
            print(slice)
        if len(destination_df) > max_rows:
            destination_df = destination_df.iloc[1:]
        if len(destination_df) == max_rows:
            print("heh")


get_corresponding_interval(df_5m, df_30m)

"""
