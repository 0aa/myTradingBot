import numpy as np


class PerformanceAnalytics:
    def __init__(self, initial_balance):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.num_trades = 0
        self.num_winning_trades = 0
        self.num_losing_trades = 0
        self.total_profit_loss = 0
        self.win_loss_ratio = 0
        self.total_holding_period = 0
        self.average_holding_period = 0
        self.daily_returns = []

    def update_trade_stats(self, trade_result, holding_period):
        self.num_trades += 1
        self.total_holding_period += holding_period

        if trade_result > 0:
            self.num_winning_trades += 1
        elif trade_result < 0:
            self.num_losing_trades += 1

        self.total_profit_loss += trade_result
        self.current_balance += trade_result

        if self.num_winning_trades > 0:
            self.win_loss_ratio = self.num_winning_trades / (self.num_winning_trades + self.num_losing_trades)

        if self.total_holding_period > 0:
            self.average_holding_period = self.total_holding_period / self.num_trades

        self.daily_returns.append(trade_result / self.initial_balance)

    def total_return(self):
        return (self.current_balance - self.initial_balance) / self.initial_balance

    def annualized_return(self, num_days):
        total_return = self.total_return()
        annualized_return = (1 + total_return) ** (365 / num_days) - 1
        return annualized_return

    def sharpe_ratio(self, risk_free_rate):
        excess_returns = np.array(self.daily_returns) - risk_free_rate
        sharpe_ratio = np.sqrt(365) * np.mean(excess_returns) / np.std(excess_returns)
        return sharpe_ratio

    def max_drawdown(self):
        peak = self.initial_balance
        max_drawdown = 0
        for daily_return in self.daily_returns:
            peak = max(peak, self.initial_balance * (1 + daily_return))
            drawdown = (peak - self.initial_balance) / peak
            max_drawdown = max(max_drawdown, drawdown)
        return max_drawdown

    def avg_daily_return(self):
        return np.mean(self.daily_returns)

    def daily_volatility(self):
        return np.std(self.daily_returns)

    def get_performance_metrics(self):
        metrics = {
            "initial_balance": self.initial_balance,
            "current_balance": self.current_balance,
            "num_trades": self.num_trades,
            "num_winning_trades": self.num_winning_trades,
            "num_losing_trades": self.num_losing_trades,
            "total_profit_loss": self.total_profit_loss,
            "win_loss_ratio": self.win_loss_ratio,
            "average_holding_period": self.average_holding_period,
            "total_return": self.total_return(),
            "annualized_return": self.annualized_return(num_days=365),
            "sharpe_ratio": self.sharpe_ratio(risk_free_rate=0),
            "max_drawdown": self.max_drawdown(),
            "avg_daily_return": self.avg_daily_return(),
            "daily_volatility": self.daily_volatility()
        }
        return metrics


    def drawdown(self):
        pass

    def sharp_caf(self):
        pass
