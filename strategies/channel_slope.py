from strategies.indicators import Indicators as Ind
import numpy as np


class ChannelSlope:

    def __init__(self, obj):

        self.dataframe = obj.dataframe
        self.trades = obj.trades
        self.bot = obj.tg_bot

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

    def set_custom_vals(self):
        """custom strategy values"""
        self.short_slope = 45
        self.long_slope = -70
        self.short_pos_in_channel = 0.9
        self.long_pos_in_channel = 0.9
        """custom indicators values"""
        self.atr_period = 8
        self.maxmin_period = 7
        self.slope_period = 29

    '''default params = [5, 5, 0.5, 0.5, 14, 10, 5]'''
    def set_custom_vals_opt(self, params):
        self.short_slope, \
        self.long_slope, \
        self.short_pos_in_channel, \
        self.long_pos_in_channel, \
        self.atr_period, \
        self.maxmin_period, \
        self.slope_period = params
        self.convert_to_right_type()

    def convert_to_right_type(self):
        self.short_slope = int(self.short_slope)
        self.long_slope = int(self.long_slope)
        self.short_pos_in_channel = self.short_pos_in_channel/10
        self.long_pos_in_channel = self.long_pos_in_channel/10
        self.atr_period = int(self.atr_period)
        self.maxmin_period = int(self.maxmin_period)
        self.slope_period = int(self.slope_period)

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
        total_profit = 0.0
        trades = {"Quantity": 0,
                  "Open_Price": 0,
                  "Total_Amount": 0}

        for index, row in prepared_df.iterrows():
            if row['Trade'] == 'BUY__':
                lot = 5
                temp_trades = {"Quantity": lot,
                               "Open_Price": row['close'],
                               "Total_Amount": row['close']*lot}

                trades["Quantity"] = trades["Quantity"] + temp_trades["Quantity"]
                trades["Total_Amount"] = trades["Total_Amount"] + temp_trades["Total_Amount"]
                trades['Open_Price'] = trades["Total_Amount"] / trades["Quantity"]
                print("Open", trades)
                # self.trades.write_pos(1, row['close'])

                self.bot.send_message(f"Open: {trades}"
                                      f"\nClose price: {row['close']}"
                                      f"\nTotal Profit: {total_profit}")

            if row['Trade'] == 'CLOSE' and trades['Open_Price'] > 0:
                profit = (float(row['close']) - float(trades['Open_Price'])) * float(trades['Quantity'])
                total_profit += profit

                print(f"Close: {trades} close price: {row['close']} profit: {profit}")

                self.bot.send_message(f"Close: {trades}"
                                      f"\nClose price: {row['close']}"
                                      f"\nProfit: {profit}"
                                      f"\nTotal Profit: {total_profit}")

                trades = {"Quantity": 0,
                          "Open_Price": 0,
                          "Total_Amount": 0}
                '''
                try:
                    open_pos = self.trades.read_positions()[0]  # FIX
                    if float(open_pos['Open_Price']) > 0:
                        profit = (float(row['close']) - float(open_pos['Open_Price'])) * float(open_pos['Quantity'])
                        #print("profit:", profit, index, " avg open price:",
                        #open_pos['Open_Price'], "close price:", row['close'], "Quantity:", open_pos['Quantity'])
                        total_profit += profit
                except:
                    pass

                self.trades.close_position()
                # profit = profit + (open_pos['Open_Price'] - row['close'])
                '''
        self.trades.close_position()
        print(total_profit)
        # print(prepared_df.to_string())
        total_profit_min = -total_profit
        return total_profit_min

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
