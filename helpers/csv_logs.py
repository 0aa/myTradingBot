"""
store deals
"""

from src.utils import get_project_root
from  pandas import *

"""
create instance if the class with the following:
    symbol: i.e ETH
    timeframe: i.e 60
    dataset limit: 100 - for different strategies   
"""

class Deals:

    def __init__(self, symbol, timeframe, limit):

        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = str(limit)
        self.root = get_project_root()
        self.file_name = f'{self.symbol}_{self.timeframe}_{self.limit}.csv'
        self.file_path = self.root / f'storage/{self.file_name}'
        self.file = self.create_deals()

    def create_deals(self):
        try:
            f = open(self.file_path, 'x')
            f.write('symbol,deal,price,count,amount\n')
            print(f"File {self.file_name} was created")
            return f
        except FileExistsError:
            print(f"File {self.file_name} already exists")

    def read_deals(self):
        return read_csv(self.file_path, 'r')

    def read_last(self):
        return open(self.file_path, 'r').readlines()[-1]

    def write_deals(self, deal, price: float, amount: float):
        string = f"{self.symbol},{deal},{price},{amount},{price*amount}\n"
        f = open(self.file_path, 'a')
        f.write(string)
        f.close()


deals = Deals("ETH", 60, 1000)
#deals.write_deals("buy", 1000, 3)
print("last:", (deals.read_deals()))
