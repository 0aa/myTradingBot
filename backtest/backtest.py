from multiprocessing import Pool
import time

from statsmodels.tools.sm_exceptions import MissingDataError

'''
    obj - strategy class with df = "Strategy(dataframe)" that has the following:
    set_random_vals() - set-up random values for Monte-Carlo
    run() - tu run thru dataframe with random values
    num_runs - number of iterations
'''


class Backtest:

    def __init__(self, obj):
        self.obj = obj
        self.num_runs = 1
        self.montecarlo = False

    '''
    static backtest is for existing static dataframe only, for live data will use live backtest  
    '''

    def run_static_backtest(self, n):
        try:
            """backtest itself"""
            if self.montecarlo: self.obj.set_random_vals()
            self.obj.run_test()

            """reporting"""
            run_params = vars(self.obj)
            run_params.pop('dataframe')
            #print(run_params)
        except:
            pass

    def run_live_backtest(self, ):
        pass

    def run_pool(self):
        pool = Pool()
        try:
            pool.imap(self.run_static_backtest, range(self.num_runs))  # <== LOOP
        except ValueError:  # raised if `y` is empty.
            pass
        finally:
            pool.close()
            pool.join()

    def drawdown(self):
        pass

    def sharp_caf(self):
        pass
