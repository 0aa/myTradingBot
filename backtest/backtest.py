from multiprocessing import Pool
import time

'''
obj - strategy class with df "Strategy(dataframe)" that has the following:
    set_random_vals() - set-up random values for Monte-Carlo
    run() - tu run thru dataframe with random values
num_runs - number of iterations
'''


class Backtest:

    def __init__(self, obj):
        self.obj = obj
        self.num_runs = 1000

    def run_pool(self):
        pool = Pool()
        pool.map(self.run_backtest, range(self.num_runs))
        pool.close()
        pool.join()
        pass

    def run_backtest(self, n):
        # create empty dataframe with results
        self.obj.set_random_vals()
        signal, price = self.obj.run()
        run_params = vars(self.obj)

    def drawdown(self):
        pass

    def sharp_caf(self):
        pass
