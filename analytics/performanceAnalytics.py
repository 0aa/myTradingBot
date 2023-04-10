import pandas as pd
import numpy as np


class TradeAnalysis:
    def __init__(self, df):
        self.df = df

    def modify_df(self):
        self.df.loc[(self.df['Signal'] == 'CLOSE'), 'Max Invest'] = self.df['Amount'] * self.df['Price']

    def num_trades(self):
        return len(self.df)

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
        total_days = (self.df['Timestamp'].iloc[-1] - self.df['Timestamp'].iloc[0]).days
        print (total_days)
        # Check if total_days is zero and return 0 to avoid ZeroDivisionError
        if total_days == 0:
            return 0
        total_return_decimal = self.total_return(initial_capital)/100
        annualized_return = ((1 + total_return_decimal) ** (num_days / total_days)) - 1
        return annualized_return

    def sharpe_ratio(self, risk_free_rate=0):
        daily_returns = self.df['Close Profit'].pct_change().dropna()
        excess_returns = daily_returns - risk_free_rate
        return excess_returns.mean() / excess_returns.std()

    def avg_daily_return(self):
        daily_returns = self.df['Close Profit'].pct_change().dropna()
        return daily_returns.mean()

    def daily_volatility(self):
        daily_returns = self.df['Close Profit'].pct_change().dropna()
        return daily_returns.std()

    def max_drawdown(self):
        if len(self.df) == 0:
            return 0
        # Calculate the cumulative returns
        cumulative_returns = (1 + self.df['Close Profit'].pct_change()).cumprod()
        # Calculate the running maximum cumulative return
        running_max = cumulative_returns.expanding().max()
        # Calculate drawdowns
        drawdowns = 1 - (cumulative_returns / running_max)
        # Find the maximum drawdown
        max_drawdown = drawdowns.max()
        return max_drawdown

    def report(self):
        return (
            f"num_trades: {self.num_trades()}\n"
            f"num_winning_trades: {self.num_winning_trades()}\n"
            f"num_losing_trades: {self.num_losing_trades()}\n"
            f"total_profit_loss: {self.total_profit_loss()}$\n"
            f"win_loss_ratio: {self.win_loss_ratio()}\n"
            f"average_holding_period: {self.average_holding_period()}\n"
            f"total_return: {self.total_return(initial_capital=10000)}%\n"
            f"annualized_return: {self.annualized_return(initial_capital=10000, num_days=365)}%\n"
            f"sharpe_ratio: {self.sharpe_ratio(risk_free_rate=0)}\n"
            f"max_drawdown: {self.max_drawdown()}\n"
            f"avg_daily_return: {self.avg_daily_return()}\n"
            f"daily_volatility: {self.daily_volatility()}"
        )
