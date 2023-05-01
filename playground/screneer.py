from finviz.screener import Screener


"""
sh_price_u50
ta_highlow20d_nh
ta_perf_4w10o
ta_perf2_52wup
ta_sma20_pa
ta_sma50_pa
"""
#['sh_price_u50', 'ta_highlow20d_nh', 'ta_perf_4w10o', 'ta_perf2_52wup', 'ta_sma20_pa', 'ta_sma50_pa']
filters = ['ta_sma50_cross200b']  # Shows companies in NASDAQ which are in the S&P500
stock_list = Screener(filters=filters, table='Performance', order='price')  # Get the performance table and sort it by price ascending

for stock in stock_list:  # Loop through 10th - 20th stocks
    print(stock['Ticker']) # Print symbol and price
print(len(stock_list))