import numpy as np


# close a part position if current price is below of stop-price - it can be stop-loss for LONG or take-profit for SHORT
def close_if_below(grid, current_price, i):
    for k in range(len(df.loc[i][grid])):
        stop_price = df.loc[i][grid][0]

        if stop_price[0] >= current_price:

            if df.loc[i]['volume'] == df.loc[i]['volume_left']:
                stop_volume = df.loc[i]['volume'] * stop_price[1] / 100
            else:
                stop_volume = df.loc[i]['volume_left'] * stop_price[1] / 100

            df.at[i, 'volume_left'] = np.round(df.loc[i]['volume_left'] - stop_volume, 2)

            # close() - pass price and volume to Binance
            # calculate profit

            if grid == "profit_grid":
                close_type = "Take Profit"
                df.at[i, 'profit'] = df.at[i, 'profit'] - stop_volume * (current_price - df.loc[i]['open_price'])
            else:
                close_type = "Stop Loss"
                df.at[i, 'profit'] = df.at[i, 'profit'] + stop_volume * (current_price - df.loc[i]['open_price'])

            print('Type', close_type, 'Closed lot:', stop_volume, ' Price:', current_price, ' Profit:',
                  df.at[i, 'profit'])

            del df.loc[i][grid][0]
            grid_len = len(df.loc[i][grid])
            if df.at[i, 'volume_left'] == 0.0:
                df.at[i, 'status'] = 'closed'


# close a part of position if current price is above of stop-price - stop-loss for SHORT or take-profit for LONG
def close_if_above(grid, current_price, i):
    for k in range(len(df.loc[i][grid])):
        stop_price = df.loc[i][grid][0]

        if stop_price[0] <= current_price:

            if df.loc[i]['volume'] == df.loc[i]['volume_left']:
                stop_volume = df.loc[i]['volume'] * stop_price[1] / 100
            else:
                stop_volume = df.loc[i]['volume_left'] * stop_price[1] / 100

            df.at[i, 'volume_left'] = np.round(df.loc[i]['volume_left'] - stop_volume, 2)

            # close() - pass price and volume to Binance

            # calculate profit
            if grid == "profit_grid":
                close_type = "Take Profit"
                df.at[i, 'profit'] = df.at[i, 'profit'] + stop_volume * (current_price - df.loc[i]['open_price'])
            else:
                close_type = "Stop Loss"
                df.at[i, 'profit'] = df.at[i, 'profit'] - stop_volume * (current_price - df.loc[i]['open_price'])

            print(close_type, 'Closed lot:', stop_volume, ' Price:', current_price, ' Profit:', df.at[i, 'profit'])

            del df.loc[i][grid][0]
            grid_len = len(df.loc[i][grid])
            if df.at[i, 'volume_left'] == 0.0:
                df.at[i, 'status'] = 'closed'