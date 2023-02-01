"""
store deals
"""

import csv
from src.utils import get_project_root


class Deals:

    def __init__(self, symbol, timeframe, limit):

        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = str(limit)
        self.root = get_project_root()
        self.file_path = self.root / f'storage/{self.symbol}_{self.timeframe}_{self.limit}.csv'
        self.file = self.create_deals()

    def create_deals(self):
        try:
            f = open(self.file_path, 'x')
            f.write('symbol,deal,price,count,amount\n')
            return f.close()

        except FileExistsError:
            print("File Already Exists")

    def read_deals(self):
        return open(self.file_path, 'r')

    def read_last(self):
        return open(self.file_path, 'r').readlines()[-1]

    def write_deals(self, deal, price: float, amount: float):
        string = f"{self.symbol},{deal},{price},{amount},{price*amount}\n"
        f = open(self.file_path, 'a')
        f.write(string)
        f.close()


deals = Deals("ETH", 60, 1000)

str = 'eth,buy,1233,2'
deals.write_deals("buy", 1000, 3)
print("last:", deals.read_last())
