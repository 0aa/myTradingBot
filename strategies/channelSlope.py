from copy import copy

import pandas as pd
from strategies.indicators import Indicators as Ind


class ChannelSlope:

    def __init__(self, data_source):
        self.dataframe = data_source.dataframe  # <= Binance class

        """default strategy values"""
        self.short_slope = 20
        self.long_slope = -20
        self.short_pos_in_channel = 0.7
        self.long_pos_in_channel = 0.3
        """custom indicators values"""
        self.rsi_period = 10
        self.maxmin_period = 15
        self.slope_period = 8
        self.introduction()

    def introduction(self):
        print("Strategy: Channel Slope")

    def set_custom_vals(self):
        """custom strategy values after optimization"""
        self.short_slope = 9.5
        self.long_slope = 3.7
        self.short_pos_in_channel = 0.34
        self.long_pos_in_channel = 0.44
        """custom indicators values"""
        self.rsi_period = 7
        self.maxmin_period = 6
        self.slope_period = 18

    '''default params = [5, 5, 0.5, 0.5, 14, 10, 5]
       custom params = [9.5, 3.7, 0.34, 0.44, 7, 6, 18]
    '''
    def set_custom_vals_opt(self, params):
        self.short_slope, \
        self.long_slope, \
        self.short_pos_in_channel, \
        self.long_pos_in_channel, \
        self.rsi_period, \
        self.maxmin_period, \
        self.slope_period = params

    def prepare_live_df(self, dataframe):
        return Ind.prepareDF_gpt(dataframe, self.rsi_period, self.maxmin_period, self.slope_period)

    def prepare_static_df(self, dataframe):
        dataframe = copy(dataframe)
        return Ind.prepareDF_gpt(dataframe, self.rsi_period, self.maxmin_period, self.slope_period)

    # find trades in the prepared dataframe
    def find_trades(self, prepared_df):

        prepared_df.loc[((prepared_df['slope'] < self.long_slope)

                         & (prepared_df['loc_min'].notna())
                         & (prepared_df['Parabolic_SAR'] < prepared_df['Close'])

                         #& (prepared_df['Parabolic_SAR_daily'] < prepared_df['Close'])
                         #& (prepared_df['MACD_per'] > 0)
                         #& (prepared_df['Aroon_Down'] < prepared_df['Aroon_Up'])
                         & (prepared_df['pos_in_ch'] < self.long_pos_in_channel)), 'Trade'] = 'BUY__'

        prepared_df.loc[((prepared_df['slope'] > self.short_slope)
                         & (prepared_df['loc_max'].notna())
                         & (prepared_df['pos_in_ch'] > self.short_pos_in_channel)), 'Trade'] = 'CLOSE'

        #prepared_df.loc[(prepared_df['Parabolic_SAR'] > prepared_df['Close']), 'Trade'] = 'STOP LOSS'

        return prepared_df

    def run(self, dataframe=pd.Series(dtype='int64')):
        prepared_df = self.prepare_live_df(dataframe) if not dataframe.empty else self.prepare_static_df(self.dataframe)
        #print(self.find_trades(prepared_df).tail(1).to_string(header=True))
        return self.find_trades(prepared_df)['Trade'].iloc[-1]
