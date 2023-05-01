import numpy as np
import pandas as pd

from strategies.indicators import Indicators
from finta import TA

"""
Strategy by twitter.com/ripster47
DRAFT/WIP
"""

class ripsterClouds:

    def __init__(self, data_source):
        self.dataframe = data_source.dataframe  # <= Binance class

        self.introduction()

    def introduction(self):
        print(f"Strategy: {self.__class__.__name__}")

    @staticmethod
    def ema(series, length):
        # Check if there are enough elements to calculate the EMA
        if len(series) < length:
            return np.nan
        # Calculate the EMA for the given series and length
        ema = series.ewm(span=length).mean()
        # Fill the first (length - 1) elements with NaN
        ema[:length - 1] = np.nan

        return ema


    @classmethod
    def create_signals(cls, data):
        data['HL2'] = (data['High'] + data['Low']) / 2

        # Cloud #1
        data['ema_8'] = cls.ema(data['HL2'], 8)
        data['ema_9'] = cls.ema(data['HL2'], 9)
        # Cloud #2
        data['ema_5'] = cls.ema(data['HL2'], 5)
        data['ema_13'] = cls.ema(data['HL2'], 13)
        # Cloud #3
        #data['ema_20'] = cls.calculate_ema(data, 20)
        #data['ema_21'] = cls.calculate_ema(data, 21)
        # Cloud #4
        data['ema_34'] = cls.ema(data['HL2'], 34)
        data['ema_50'] = cls.ema(data['HL2'], 50)

        data['ema_72'] = cls.ema(data['HL2'], 72)
        data['ema_89'] = cls.ema(data['HL2'], 89)

        data['ROC'] = TA.ROC(data, 72)

        data['ema_34_slope'] = Indicators.indSlope_gpt(data['ema_34'], 8)  # <====try to optimize
        return data

    def prepare_live_dataframe(self, dataframe):
        return self.create_signals(dataframe)

    @staticmethod
    def prepare_static_dataframe(data):
        return ripsterClouds.create_signals(data)

    @staticmethod
    def find_trades(data):
        data.loc[(data['ema_5'] > data['ema_13'])
                 & (data['ema_34'] > data['ema_50'])

                 & (data['ema_34_slope'] > 40)

                 & (data['ROC'] > 0)

                 & (data['ema_72'] > data['ema_89'])

                 & (data['ema_8'] > data['ema_9'])
                 & (data['Close'] > data['ema_72']), "Trade"] = "BUY"

        data.loc[(data['ema_8'] < data['ema_9'])
                 & (data['ema_5'] < data['ema_13']), "Trade"] = "CLOSE"

        return data

    def run(self, df=pd.Series(dtype='int64')):
        prepared_dataframe = self.prepare_live_dataframe(df) if not df.empty else self.prepare_static_dataframe()
        prepared_dataframe = self.find_trades(prepared_dataframe)
        #print(prepared_dataframe.to_string(header=True))
        #print(prepared_dataframe.tail(11).to_string(header=True))

        #print(prepared_dataframe['Timestamp'].iloc[-1])
        return self.find_trades(prepared_dataframe)['Trade'].iloc[-1]
