import pandas as pd
import numpy as np


class TradeAnalysis:
    def __init__(self, df):
        self.df = df

    def modify_df(self):
        self.df.loc[(self.df['Signal'] == 'CLOSE'), 'Max Invest'] = self.df['Amount'] * self.df['Price']
        self.df.fillna(value=np.nan, inplace=True)

    def num_trades(self):
        return len(self.df)

    def num_days(self):
        return (self.df['Timestamp'].iloc[-1] - self.df['Timestamp'].iloc[0]).days

    def num_winning_trades(self):
        return len(self.df[self.df['Close Profit'] > 0])

    def num_losing_trades(self):
        return len(self.df[self.df['Close Profit'] < 0])

    def total_profit_loss(self):
        return self.df['Close Profit'].sum()

    def win_loss_ratio(self):
        winning_trades = self.num_winning_trades()
        losing_trades = self.num_losing_trades()
        return winning_trades / losing_trades if losing_trades != 0 else np.inf

    def average_holding_period(self):
        pass

    def total_return(self, initial_capital):
        if len(self.df) == 0:
            return 0
        total_profit = self.df['Close Profit'].sum()
        total_return = total_profit / initial_capital
        return total_return

    def annualized_return(self, initial_capital, num_days=365):
        if len(self.df) == 0:
            return 0
        total_days = self.num_days()
        # Check if total_days is zero and return 0 to avoid ZeroDivisionError
        if total_days == 0:
            return 0
        total_return_decimal = self.total_return(initial_capital)
        annualized_return = ((1 + total_return_decimal) ** (num_days / total_days)) - 1
        return annualized_return

    def sharpe_ratio(self, risk_free_rate=0):
        daily_returns = self.df['Close Profit'].pct_change().dropna()
        excess_returns = daily_returns - risk_free_rate
        return excess_returns.mean() / excess_returns.std()

    def sharpe_ratio_meaning(self):
        ratio = self.sharpe_ratio()
        if ratio < 1:
            return "Poor"
        elif 1 <= ratio < 2:
            return "Good"
        else:
            return "Excellent"

    def avg_daily_return(self):
        daily_returns = self.df['Close Profit'].pct_change().dropna()
        return daily_returns.mean()

    def avg_daily_volatility(self):
        daily_returns = self.df['Close Profit'].pct_change().dropna()
        return daily_returns.std()

    def calculate_drawdown(self):
        if len(self.df) == 0:
            return 0

        # Calculate the cumulative maximum of the "Total Profit" column
        cum_max = self.df['Total Profit'].cummax()

        # Set the drawdown to NaN where the cumulative maximum is zero
        drawdown = (self.df['Total Profit'] - cum_max) / np.where(cum_max == 0, np.nan, cum_max)
        return drawdown.min() * 100

    def report(self):
        return (
            f"Trades: {self.num_trades()}\n"
            f"Days:{self.num_days()}\n"
            f"Winning Trades: {self.num_winning_trades()}\n"
            f"Losing Trades: {self.num_losing_trades()}\n"
            f"Total Profit Loss: {round(self.total_profit_loss(),2)} USD\n"
            f"Win/Loss Ratio: {self.win_loss_ratio()}\n"
            f"Average Holding Period: {self.average_holding_period()}\n"
            f"Total Return: {round(self.total_return(initial_capital=5000) * 100, 2)}%\n"
            f"Annualized Return: {round(self.annualized_return(initial_capital=5000, num_days=365) * 100, 2)}%\n"
            f"Sharpe Ratio: {round(self.sharpe_ratio(risk_free_rate=0.04), 3)} => {self.sharpe_ratio_meaning()}\n"
            f"Max Drawdown: {round(self.calculate_drawdown(), 2)}%\n"
            f"Avg Daily Return: {round(self.avg_daily_return(), 2)}%\n"
            f"Avg Daily Volatility: {round(self.avg_daily_volatility(), 2)}"
        )
