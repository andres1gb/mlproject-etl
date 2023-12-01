import argparse
import datetime
import json
import csv
import os

from dateutil.relativedelta import relativedelta

from extractor import DEFAULT_MONTH_FROM
from utils.dates import MonthString


class Loader:
    @classmethod
    def load_data(cls, start, end):
        dest = open('data/complete.csv', 'w')
        writer = csv.writer(dest)
        headers = ['day'] + Loader.extract_headers(start, end)
        writer.writerow(headers)

        for day, data in Loader.read_range(start, end):
            row = {}
            data['day'] = day
            for key in headers:
                if key not in data:
                    row[key] = None
                else:
                    row[key] = data[key]
            writer.writerow(list(row.values()))

        dest.close()

    @classmethod
    def extract_headers(cls, start, end):
        keys = []
        for day, row in Loader.read_range(start, end):
            new_keys = list(row.keys())
            for key in new_keys:
                if not key in keys:
                    keys.append(key)
        return keys

    @classmethod
    def read_range(cls, start, end):
        current = MonthString.to_datetime(start)
        end = MonthString.to_datetime(end)
        while current <= end:
            dirname = os.path.join(os.path.dirname(__file__), 'data/transformed/')
            filename = os.path.join(dirname, MonthString.from_date(current, '-') + '.json')
            source = open(filename, "r")
            rows = json.load(source)
            for row in rows:
                yield row, rows[row]
            source.close()
            current = current + relativedelta(months=1)


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
