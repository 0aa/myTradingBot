import math
from random import random

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf

from strategies.ripsterClouds import ripsterClouds

yf.pdr_override()

# Function to calculate moving averages
def moving_average(series, length):
    # Check if there are enough elements to calculate the EMA
    if len(series) < length:
        return np.nan
    # Calculate the EMA for the given series and length
    ema = series.ewm(span=length).mean()
    # Fill the first (length - 1) elements with NaN
    ema[:length - 1] = np.nan
    return ema


SYMBOL = 'AFIB'
START_TIME = '2023-3-1'
END_TIME = '2023-4-1'

df = pdr.get_data_yahoo(SYMBOL, start=START_TIME, end=END_TIME, interval='1h')

df.reset_index(inplace=True)
df.rename(columns={'Datetime': 'Timestamp'}, inplace=True)
df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]

df['HL2'] = (df['High'] + df['Low']) / 2


# Calculate moving averages
ma_len_list = [8, 9, 5, 13, 34, 50, 72, 89]
ma_data = [moving_average(df['HL2'], length) for length in ma_len_list]

df = ripsterClouds.create_signals(df)
df = ripsterClouds.find_trades(df)



# Plotting
fig, ax1 = plt.subplots(1, 1, figsize=(14, 5), sharex=True)

ax1.plot(df.index, df['Close'], label='Close Price', color='black', linewidth=1)

colors = ['#036103', '#880e4f', '#4caf50', '#f44336', '#2196f3', '#ffb74d', '#009688', '#f06292', '#05bed5', '#e65100']
for i in range(0, len(ma_data), 2):
    ax1.fill_between(df.index, ma_data[i], ma_data[i+1], where=ma_data[i] >= ma_data[i+1], facecolor=colors[i], alpha=0.65)
    ax1.fill_between(df.index, ma_data[i], ma_data[i+1], where=ma_data[i] < ma_data[i+1], facecolor=colors[i+1], alpha=0.65)

print(df.to_string())

green_area = (df['Trade'] == 'BUY')
for idx, value in enumerate(green_area):
    if value:
        ax1.axvline(x=idx, color='green', alpha=0.2)

green_area = (df['Trade'] == 'CLOSE')
for idx, value in enumerate(green_area):
    if value:
        ax1.axvline(x=idx, color='red', alpha=0.2)


ax1.set_xlabel('Timestamp')
ax1.set_ylabel('Price')
ax1.set_title(f'{SYMBOL} Stock Price with EMA Clouds')
ax1.legend()

#ax2.plot(df.index, df['ROC'], label='ROC', color='green')
#ax2.set_xlabel('Date')
#ax2.set_ylabel('ROC (%)')
#ax2.legend(loc='best')

plt.show()
