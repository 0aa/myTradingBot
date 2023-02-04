import csv
import os
from src.utils import get_project_root


def read_positions_from_csv(file_path):
    positions = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Status'] != 'Closed':
                    positions.append(row)
    else:
        raise Exception(f"File not found: {file_path}")
    return positions


def write_positions_to_csv(file_path, positions):
    with open(file_path, 'a') as csvfile:
        fieldnames = ['Symbol', 'Quantity', 'Open_Price', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for position in positions:
            writer.writerow(position)


def check_close_position(position, target_profit, stop_loss, current_price):

    if current_price >= float(position['Open_Price']) + float(target_profit):
        # Close position if target profit is reached
        position['Status'] = 'Closed'
        return True
    elif current_price <= float(position['Open_Price']) - float(stop_loss):
        # Close position if stop loss is reached
        position['Status'] = 'Closed'
        return True
    else:
        return False


file_path = get_project_root() / f'storage/positions.csv'
loaded_positions = read_positions_from_csv(file_path)
target_profit = 5.00
stop_loss = 10.00

positions = [
    {'Symbol': 'AAPL', 'Quantity': 100, 'Open_Price': 145.00, 'Status': 'Open'},
    {'Symbol': 'AAPL', 'Quantity': 50, 'Open_Price': 147.00, 'Status': 'Open'}
]

write_positions_to_csv(file_path, positions)

'''
for position in loaded_positions:
    current_price = 147.00
    if check_close_position(position, target_profit, stop_loss, current_price):
        print(f"Close position for {position['Symbol']}")
    else:
        print(f"Keep position open for {position['Symbol']}")

write_positions_to_csv(file_path, loaded_positions)
'''