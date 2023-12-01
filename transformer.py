# Data from data/aemet
# Every file contains a whole month, which means that there are multiple entries for each day belonging to that month.
# Since we want to analyze the whole day, we should create a column per target value per station
# i.e. for the file for month 2021-01 (January 2021), there would be multiple inputs for day number 1. We should create
# an entry for the date 2020-01-01 and add columns in the format <station_code>-<value_name>:
#
# Date          4358X-sun_hours 4358X-wind_avg 4358X-wind_max ... C447A-sun_hours C447A-wind_avg C447A-wind_max ...
# 2020-01-01    8.2             0.3            2.8                6.4             4.2             12.8
# 2020-01-02    ...
# ...
# 2020-01-30    ...
#
# In this example, 4358X is the code for DON BENITO (BADAJOZ) station and C447A is TENERIFE NORTE AEROPUERTO
# (STA. CRUZ DE TENERIFE). Notice that not all stations retrieves every possible parameter and there could be
# dates where some station values are missing (i.e. for maintenance operations).
#
# Since the number of columns can be very big, excluding values or even stations would be considered. Nevertheless,
# the purpose of the machine learning approach is not to reduce the input data to those values that economic analysis
# suggest a priori that would be of use (prime regions with bigger plants of solar/wind), and let the engine
# learn from a bigger dataset.
#
import argparse
import datetime
import json
import os

from extractor import DEFAULT_MONTH_FROM
from sources import aemet, ree
from utils.dates import MonthString
from dateutil.relativedelta import relativedelta

from utils.logger import Logger


class Transformer:
    @classmethod
    def transform_data(cls, start, end):
        current = MonthString.to_datetime(start)
        end = MonthString.to_datetime(end)

        while current <= end:
            # read aemet data for current month
            data = aemet.Extractor.get_data_from_file(current)
            # loop over data adding key:val data for every date
            if len(data) > 0:
                day = ''
                result = {}
                for station in data:
                    if station['fecha'] != day:
                        day = station['fecha']
                        result[day] = {}
                        prices = ree.Extractor.get_data_from_file(day)
                        price = 0
                        if prices['included'][0]['id'] == "600":
                            spot_prices = prices['included'][0]['attributes']['values']
                        else:  # since 2021-05-31, PVPC and spot prices are included
                            spot_prices = prices['included'][1]['attributes']['values']
                        for hour in range(0, 24):
                            price += spot_prices[hour]['value']
                        result[day]['price'] = price/24
                    prefix = station['indicativo']
                    if 'tmin' in station:
                        result[day][prefix + '_t_min'] = float(station['tmin'].replace(",", "."))
                    if 't_avg' in station:
                        result[day][prefix + '_t_avg'] = float(station['tmed'].replace(",", "."))
                    if 'tmax' in station:
                        result[day][prefix + '_t_max'] = float(station['tmax'].replace(",", "."))
                    if 'velmedia' in station:
                        result[day][prefix + '_w_avg'] = float(station['velmedia'].replace(",", "."))
                    if 'racha' in station:
                        result[day][prefix + '_w_max'] = float(station['racha'].replace(",", "."))
                    if 'sol' in station:
                        result[day][prefix + '_sun'] = float(station['sol'].replace(",", "."))
            # save result
            dirname = os.path.join(os.path.dirname(__file__), 'data/transformed/')
            filename = os.path.join(dirname, MonthString.from_date(current, '-') + '.json')
            with open(filename, 'w') as f:
                json.dump(result, f)
            current = current + relativedelta(months=1)

def parse_args():
    parser = argparse.ArgumentParser(
        prog='transformer.py',
        description='Prepares data from Aemet and REE for analysis',
        epilog='Created by Andrés Purriños 2023'
    )
    current_month = MonthString.from_date(datetime.datetime.now())
    parser.add_argument('-f', default=DEFAULT_MONTH_FROM, help='First month to import (YYYY-MM format)')
    parser.add_argument('-t', default=current_month, help='Last month to import (YYYY-MM format)')
    return vars(parser.parse_args())


if __name__ == '__main__':
    args = parse_args()

    start = args['f']
    end = args['t']

    Transformer.transform_data(start, end)
    # Transformer.transform_data('2021-05', '2021-05')

