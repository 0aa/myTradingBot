import pandas as pd

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
    def calculate_ema(data, window):
        return data['Close'].ewm(span=window).mean()

    def create_signals(self, data):
        data['ema_5'] = self.calculate_ema(data, 5)
        data['ema_12'] = self.calculate_ema(data, 12)
        data['ema_34'] = self.calculate_ema(data, 34)
        data['ema_50'] = self.calculate_ema(data, 50)
        data['ema_8'] = self.calculate_ema(data, 8)
        data['ema_9'] = self.calculate_ema(data, 9)
        data['ema_20'] = self.calculate_ema(data, 20)
        data['ema_21'] = self.calculate_ema(data, 21)
        return data

    def prepare_live_dataframe(self, dataframe):
        return self.create_signals(dataframe)

    def prepare_static_dataframe(self):
        return self.dataframe

    def find_trades(self, prepared_df):
        prepared_df.loc[(prepared_df['ema_5'] > prepared_df['ema_12'])
                        & (prepared_df['ema_34'] > prepared_df['ema_50'])
                        & (prepared_df['ema_8'] > prepared_df['ema_9'])
                        & (prepared_df['ema_20'] > prepared_df['ema_21']), "Trade"] = "BUY"

        prepared_df.loc[(prepared_df['ema_5'] < prepared_df['ema_12'])
                        & (prepared_df['ema_34'] < prepared_df['ema_50'])
                        & (prepared_df['ema_8'] < prepared_df['ema_9'])
                        & (prepared_df['ema_20'] < prepared_df['ema_21']), "Trade"] = "CLOSE"

        return prepared_df

    def run(self, df=pd.Series(dtype='int64')):
        prepared_dataframe = self.prepare_live_dataframe(df) if not df.empty else self.prepare_static_dataframe()
        #print(self.find_trades(prepared_dataframe).tail(1).to_string(header=True))
        return self.find_trades(prepared_dataframe)['Trade'].iloc[-1]
