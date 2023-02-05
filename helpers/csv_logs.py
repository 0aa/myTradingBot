"""
store deals
"""

from src.utils import get_project_root
import csv

from pandas import *

"""
create instance if the class with the following:
    symbol: i.e ETH
    timeframe: i.e 60
    dataset limit: 100 - for different strategies   
"""


class Trades:

    def __init__(self, symbol, timeframe, limit):

        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = str(limit)
        self.fieldnames = ['Symbol', 'Quantity', 'Open_Price', 'Total_Amount', 'Status']
        self.root = get_project_root()
        self.file_name = f'{self.symbol}_{self.timeframe}_{self.limit}.csv'
        self.file_path = self.root / f'storage/{self.file_name}'
        self.create_csvfile()

    def create_csvfile(self):
        try:
            csvfile = open(self.file_path, 'x')
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            print(f"File {self.file_name} was created")

        except FileExistsError:
            print(f"File {self.file_name} already exists")

    """return everything from the file"""

    def all_positions(self):
        return read_csv(self.file_path, 'r')

    def read_positions(self):
        positions = []
        try:
            with open(self.file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['Status'] != 'Closed':
                        positions.append(row)
        except FileNotFoundError:
            raise Exception(f"File not found: {self.file_path}")
        return positions

    def read_last(self):
        return open(self.file_path, 'r').readlines()[-1]

    def write_pos(self, quantity: float, open_price: float):
        positions = {'Symbol': self.symbol,
                     'Quantity': quantity,
                     'Open_Price': open_price,
                     'Total_Amount': open_price * quantity,
                     'Status': 'Open'}

        f = open(self.file_path, 'a')
        writer = csv.DictWriter(f, fieldnames=self.fieldnames)
        writer.writerow(positions)
        f.close()

    def write_positions_to_csv(self, position):
        csvfile = open(self.file_path, 'a+r')
        pos = read_positions()

        writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
        writer.writerow(position)
        csvfile.close()


deals = Trades("ETH", 60, 1000)
deals.write_pos(1000, 3.55)
deals.write_pos(1000, 3.60)


print("last:", (deals.read_positions()))
