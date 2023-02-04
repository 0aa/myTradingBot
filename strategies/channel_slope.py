from indicators.indicators import Indicators as Ind
import numpy as np
from helpers.csv_logs import Deals


class ChannelSlope:

    def __init__(self, dataframe):

        self.dataframe = dataframe

        """create file where we're going to keep deals"""
        self.deals = Deals("test", 100, '5m')

        """default strategy values"""
        self.long_slope = None
        self.short_slope = None
        self.short_pos_in_channel = None
        self.long_pos_in_channel = None
        """default indicators values"""
        self.atr_period = None
        self.maxmin_period = None
        self.slope_period = None
        """set all values to default"""
        self.set_default_vals()  # set the values to default

    def set_default_vals(self):
        """default strategy values"""
        self.short_slope = 5
        self.long_slope = 5
        self.short_pos_in_channel = 0.5
        self.long_pos_in_channel = 0.5
        """default indicators values"""
        self.atr_period = 14
        self.maxmin_period = 10
        self.slope_period = 5

    def prepare_df(self):
        return Ind.PrepareDF(self.dataframe, self.atr_period, self.maxmin_period)

    """update strategy and indicators values with random values"""

    def set_random_vals(self):
        # optimization with Monte-Carlo method
        # random slope
        random_slope = np.random.uniform(10, 90)
        self.short_slope = 100 - np.random.default_rng().noncentral_chisquare(3, random_slope)
        self.long_slope = 0 - np.random.default_rng().noncentral_chisquare(3, random_slope)
        # random pos in channel
        random_pos_in_channel = np.random.uniform(0, 50)
        self.short_pos_in_channel = (100 - np.random.default_rng().noncentral_chisquare(3,
                                                                                        random_pos_in_channel)) * 0.01
        self.long_pos_in_channel = np.random.default_rng().noncentral_chisquare(3, random_pos_in_channel) * 0.01

        # indicators optimization
        self.atr_period = int(np.random.default_rng().normal(14, 2))
        self.maxmin_period = int(np.random.default_rng().normal(10, 2))
        self.slope_period = int(np.random.default_rng().normal(5, 2))

    # wip
    def run_test(self):

        prepared_df = self.prepare_df()

        prepared_df.loc[((prepared_df['slope'] < - self.long_slope)
                         & (prepared_df['loc_min'].notna())
                         & (prepared_df['ATR'].notna())
                         & (prepared_df['pos_in_ch'] < self.long_pos_in_channel)), 'Trade'] = 'BUY__'

        prepared_df.loc[((prepared_df['slope'] > self.short_slope)
                         & (prepared_df['loc_max'].notna())
                         & (prepared_df['ATR'].notna())
                         & (prepared_df['pos_in_ch'] > self.short_pos_in_channel)), 'Trade'] = 'CLOSE'

        """test with line by line and deals file"""
        for index, row in prepared_df.iterrows():

            if row['Trade'] == 'BUY__':
                self.deals.write_deals('buy', -row['close'], 1)
                print('row -1', row['close'][-1])
            
            elif row['Trade'] == 'CLOSE':
                self.deals.write_deals('close', +row['close'], 1)
                #print('CLOSE', row['loc_max'])
                pass

        # prepared_df.loc[(prepared_df['Trade'] == 'BUY__', "Balance")] = - prepared_df['loc_min']

        # print(prepared_df.to_string())
        return prepared_df

    """run strategy with default or updated values"""

    """
    if "long" we buy -> "position" == price 
    if "short" && position we sell -> current price - "position"
    if  
    """

    def position(self, prepared_df):
        # buy if signal is Long
        prepared_df.loc[(prepared_df['Trade'] == "Long", "Pos")] = prepared_df['close']
        prepared_df.loc[(prepared_df['Trade'] == "Long", "Pos")]

        return prepared_df

    def run(self):
        prepared_df = self.prepare_df()

        # print(prepared_df.to_string())
        signal = None
        if (prepared_df['loc_min'][-1] > 0) and (prepared_df['pos_in_ch'][-1] < self.long_pos_in_channel) and (
                prepared_df['slope'][-1] < - self.long_slope):
            # found a good enter point for LONG
            signal = 'long'
        if (prepared_df['loc_max'][-1] > 0) and (prepared_df['pos_in_ch'][-1] > self.short_pos_in_channel) and (
                prepared_df['slope'][-1] > self.short_slope):
            # found a good enter point for SHORT
            signal = 'short'
        return signal, prepared_df.at[-1, 'close']
