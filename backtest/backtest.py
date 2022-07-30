class Backtest:

    obj = None
    num_runs = 1000

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
