from multiprocessing import Pool

class Backtest:

    def __init__(self, obj):
        self.obj = obj
        self.num_runs = 1000

    def run_backtest(self):




    def run_loop(self):
        # create empty dataframe with results
        for i in range(self.num_runs):
            self.obj.set_default_vals()
            self.obj.run()
            run_params = vars(self.obj)

    def drawdown(self):
        pass

    def sharp_caf(self):
        pass
