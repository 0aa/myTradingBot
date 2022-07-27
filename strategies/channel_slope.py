from indicators.indicators import Indicators as Ind
import numpy as np


class ChannelSlope:
    """default strategy values"""
    short_slope = 5
    long_slope = 5
    short_pos_in_channel = 0.5
    long_pos_in_channel = 0.5

    """update strategy values with random values"""
    @classmethod
    def set_random_vals(cls):
        # optimization with Monte-Carlo method
        # random slope
        random_slope = np.random.uniform(10, 90)
        cls.short_slope = 100 - np.random.default_rng().noncentral_chisquare(3, random_slope)
        cls.long_slope = 0 - np.random.default_rng().noncentral_chisquare(3, random_slope)
        # random pos in channel
        random_pos_in_channel = np.random.uniform(0, 50)
        cls.short_pos_in_channel = (100 - np.random.default_rng().noncentral_chisquare(3,
                                                                                       random_pos_in_channel)) * 0.01
        cls.long_pos_in_channel = np.random.default_rng().noncentral_chisquare(3, random_pos_in_channel) * 0.01

    """run strategy with default or updated values"""
    @classmethod
    def channel_slope(cls, dataframe):
        prepared_df = Ind.PrepareDF(dataframe)
        signal = None  # return value
        i = len(prepared_df) - 1  # 99  is current kandel which is not closed, 98 is last closed kandel, we need 97 to
        # check if it is bottom or top
        if Ind.isLCC(prepared_df, i - 1) > 0:
            # found bottom - OPEN LONG
            if prepared_df['position_in_channel'][i - 1] < cls.long_pos_in_channel:
                # close to top of channel
                if prepared_df['slope'][i - 1] < - cls.long_slope:
                    # found a good enter point for LONG
                    signal = 'long'
        if Ind.isHCC(prepared_df, i - 1) > 0:
            # found top - OPEN SHORT
            if prepared_df['position_in_channel'][i - 1] > cls.short_pos_in_channel:
                # close to top of channel
                if prepared_df['slope'][i - 1] > cls.short_slope:
                    # found a good enter point for SHORT
                    signal = 'short'
        return signal, prepared_df.at[i, 'close']