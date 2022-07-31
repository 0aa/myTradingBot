

class Backtest:

    def __init__(self, obj):
        self.obj = obj
        self.num_runs = 1000

    @classmethod
    def runt_backtest(cls):

        # create empty dataframe with results

        for i in range(cls.num_runs):
            cls.obj.set_default_vals()
            cls.obj.run()
            run_params = vars(cls.obj)





    def drawdown(self):
        pass

    def sharp_caf(self):
        pass
