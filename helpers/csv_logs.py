"""
store open positions
"""
import time

from src.utils import get_project_root
import csv

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

    '''return positions from the file'''

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

    # wip
    def close_position(self):
        summ = {'Symbol': self.symbol,
                'Quantity': 0,
                'Open_Price': 0,
                'Total_Amount': 0,
                'Status': 'Open'}
        self.rewrite_pos(summ)
        pass

    ''' summ all the positions from file and write as one line '''
    def sum_positions(self):
        positions = self.read_positions()
        summ = {'Symbol': self.symbol,
                'Quantity': 0,
                'Open_Price': 0,
                'Total_Amount': 0,
                'Status': 'Open'}
        for pos in positions:
            summ['Quantity'] = summ['Quantity'] + float(pos['Quantity'])
            summ['Total_Amount'] = summ['Total_Amount'] + float(pos['Total_Amount'])
        summ['Open_Price'] = summ['Total_Amount'] / summ['Quantity']
        self.rewrite_pos(summ)

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
        self.sum_positions()

    ''' delete everything from the file and rewrite with the new data '''

    def rewrite_pos(self, position):
        csvfile = open(self.file_path, 'w')
        pos = self.read_positions()
        writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
        writer.writeheader()
        writer.writerow(position)
        csvfile.close()



'''
deals = Trades("ETH", 60, 1000)
deals.write_pos(100, 4)
deals.write_pos(100, 2)

trades = {"Quantity": 0,
          "Open_Price": 0,
          "Total_Amount": 0}

temp_trades = {"Quantity": 1,
               "Open_Price": 100,
               "Total_Amount": 100}

trades["Quantity"] = trades["Quantity"] + temp_trades["Quantity"]
trades["Total_Amount"] = trades["Total_Amount"] + temp_trades["Total_Amount"]
trades['Open_Price'] = trades["Total_Amount"] / trades["Quantity"]

temp_trades = {"Quantity": 1,
               "Open_Price": 120,
               "Total_Amount": 120}

trades["Quantity"] = trades["Quantity"] + temp_trades["Quantity"]
trades["Total_Amount"] = trades["Total_Amount"] + temp_trades["Total_Amount"]
trades['Open_Price'] = trades["Total_Amount"] / trades["Quantity"]
print(trades)
'''