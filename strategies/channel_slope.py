from indicators.indicators import Indicators as Ind


def channel_slope(df):
    prepared_df = Ind.PrepareDF(df)
    signal = None  # return value
    i = len(prepared_df) - 1  # 99  is current kandel which is not closed, 98 is last closed candel, we need 97 to
    # check if it is bottom or top

    if Ind.isLCC(prepared_df, i - 1) > 0:
        # found bottom - OPEN LONG
        if prepared_df['position_in_channel'][i - 1] < 0.5:
            # close to top of channel
            if prepared_df['slope'][i - 1] < -20:
                # found a good enter point for LONG
                signal = 'long'

    if Ind.isHCC(prepared_df, i - 1) > 0:
        # found top - OPEN SHORT
        if prepared_df['position_in_channel'][i - 1] > 0.5:
            # close to top of channel
            if prepared_df['slope'][i - 1] > 20:
                # found a good enter point for SHORT
                signal = 'short'

    return signal, prepared_df.at[i, 'close']
