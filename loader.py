import argparse
import datetime
import json
import csv
import os

from extractor import DEFAULT_MONTH_FROM
from utils.dates import MonthString
from dateutil.relativedelta import relativedelta

from utils.logger import Logger


class Loader:
    @classmethod
    def load_data(cls, start, end):
        current = MonthString.to_datetime(start)
        end = MonthString.to_datetime(end)
        dest = open('data/complete.csv', 'w')
        writer = csv.writer(dest)
        headers_written = False

        while current <= end:
            dirname = os.path.join(os.path.dirname(__file__), 'data/transformed/')
            filename = os.path.join(dirname, MonthString.from_date(current, '-') + '.json')
            source = open(filename, "r")
            data = json.load(source)
            source.close()

            for day in data:
                if not headers_written:
                    header = data[day].keys()
                    writer.writerow(header)
                    headers_written = True
                writer.writerow(data[day])

            current = current + relativedelta(months=1)
        dest.close()

def parse_args():
    parser = argparse.ArgumentParser(
        prog='loader.py',
        description='Loads transformed data to a CSV file readable by R',
        epilog='Created by Andrés Purriños 2023'
    )
    current_month = MonthString.from_date(datetime.datetime.now())
    parser.add_argument('-f', default=DEFAULT_MONTH_FROM, help='First month to load (YYYY-MM format)')
    parser.add_argument('-t', default=current_month, help='Last month to load (YYYY-MM format)')
    return vars(parser.parse_args())


if __name__ == '__main__':
    args = parse_args()

    start = args['f']
    end = args['t']

    Loader.load_data(start, end)

