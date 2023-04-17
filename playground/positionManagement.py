import pandas as pd

from utils.telegramBot import TelegramBot


class PositionManagement:

    def __init__(self, strategy):
        self.strategy = strategy  # <= strategy class
        self.statistics_dataframe = pd.DataFrame(columns=['Timestamp', 'Signal', 'Price', 'Amount', 'Close Profit',
                                                          'Total Profit'])
        self.total_profit = 0
        self.positions = []  # list of currently open positions

        self.max_amount = 5000
        self.max_positions = 5  # maximum number of positions that can be open simultaneously
        self.stop_loss = 0.985
        self.take_profit = 1.05
        self.lot_one = 1.75
        self.lot_two = 0.75
        self.lot_three = 0.5

        self.tg_switch = False
        self.tg_bot = TelegramBot()
        self.introduction()



    def introduction(self):
        text = (f"Max Investments: {self.max_amount}"
                f"\nMax Positions: {self.max_positions}"
                f"\nStrategy: {self.strategy.__class__.__name__}")
        self.tg_switch and self.tg_bot.send_message(text)

    def apply_strategy(self, destination_df):
        try:
            signal = self.strategy.run(destination_df)

            if signal or len(self.positions) > 0:

                current_price, current_time = PositionManagement.get_current_price_and_time(destination_df)
                average_price = self.average_price_of_open_positions(current_price)

                # check if stop loss
                if self.is_stop_loss_or_take_profit(current_price, average_price):
                    signal = "STOP LOSS"

                if signal == 'BUY__' and len(self.positions) < self.max_positions:
                    return self.handle_buy_signal(signal, current_price, current_time)
                elif signal in ('CLOSE', 'STOP LOSS', 'TAKE PROFIT'):
                    return self.handle_close_signal(signal, current_price, current_time)
        except Exception as e:
            self.tg_bot.send_message(f"Error while applying strategy: {e}")
            raise Exception(f'"Error while applying strategy')

    def handle_buy_signal(self, signal, current_price, current_time):
        buy_amount = self.get_buy_amount()
        total_investments = sum(
            [amount * price for amount, price in self.positions]) + buy_amount * current_price
        if total_investments < self.max_amount:
            self.positions.append((buy_amount, current_price))
            self.record_statistics(signal, current_time, current_price, buy_amount)
            """return data required for API request to exchange"""
            return {"side": "BUY", "type": "MARKET", "quantity": buy_amount}

    def handle_close_signal(self, signal, current_price, current_time):
        if len(self.positions) > 0:
            close_profit, sell_amount = self.calculate_close_profit_and_total_amount(current_price)
            self.positions = []
            self.record_statistics(signal, current_time, current_price, sell_amount, close_profit)
            """return data required for API request to exchange"""
            return {"side": "SELL", "type": "MARKET", "quantity": sell_amount}

    @staticmethod
    def get_current_price_and_time(destination_df):
        current_price = destination_df['Close'].iloc[-1]
        current_time = destination_df['Timestamp'].iloc[-1]
        return current_price, current_time

    def average_price_of_open_positions(self, current_price):
        if len(self.positions) > 0:
            average_price = sum([amount * price for amount, price in self.positions]) / sum(
                [amount for amount, _ in self.positions])
        else:
            return current_price
        return average_price

    def is_stop_loss_or_take_profit(self, current_price, average_price):
        return (current_price / average_price < self.stop_loss or
                current_price / average_price > self.take_profit)

    def record_statistics(self, signal, current_time, current_price, amount, close_profit=None):
        new_row = pd.DataFrame({'Timestamp': [current_time], 'Signal': [signal], 'Price': [current_price],
                                'Amount': [amount], 'Close Profit': [close_profit],
                                'Total Profit': [self.total_profit]})
        self.statistics_dataframe = pd.concat([self.statistics_dataframe, new_row], ignore_index=True)
        text = (f"Found a Signal: {signal}"
                f"\nTime: {current_time}"
                f"\nPrice: {current_price}"
                f"\nLot Size: {amount}"
                f"\nOpen Positions: {self.positions}"
                f"\nTotal Profit: {round(self.total_profit, 2)}")
        self.tg_switch and self.tg_bot.send_message(text)

    def get_buy_amount(self):
        if len(self.positions) == 0:
            return self.lot_one
        elif len(self.positions) == 1:
            return self.lot_two
        else:
            return self.lot_three

    def calculate_close_profit_and_total_amount(self, current_price):
        close_profit = 0
        total_amount = 0
        for buy_amount, position_price in self.positions:
            profit = buy_amount * (current_price - position_price)
            self.total_profit += profit
            close_profit += profit
            total_amount += buy_amount
        return close_profit, total_amount
