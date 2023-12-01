import datetime
import os
import json
import requests
from dateutil.relativedelta import relativedelta
from utils.dates import MonthString
from utils.logger import Logger


class Extractor:
    # https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date=2021-01-01T00:00&end_date=2021-01-02T23:59&time_trunc=hour
    URL = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real?start_date=%s&end_date=%s&time_trunc=hour"

    @classmethod
    def get_data(cls, start, end):
        print("Downloading REE data from %s to %s" % (start, end))
        start = MonthString.first_day(start, '-')
        end = MonthString.last_day(end, '-')
        now = datetime.datetime.now()
        if start > now:
            raise ValueError("Start date is in the future")

        if end > now:
            end = now

        current = start
        while current < end:
            limit = current + relativedelta(days=1)

            start_date = current.strftime("%Y-%m-%dT00:00")
            end_date = limit.strftime("%Y-%m-%dT00:00")

            url = Extractor.URL % (start_date, end_date)
            headers = {
                "accept": "application/json"
            }
            result = requests.get(url, headers=headers)
            if result.status_code != 200:
                Logger.log(
                    "Error downloading data for date %s. Response code: %d" % (start_date, result.status_code))
                return False

            dirname = os.path.join(os.path.dirname(__file__), '../data/extracted/ree')
            filename = os.path.join(dirname, "%d-%s-%s" % (current.year, str(current.month).zfill(2),
                                                           str(current.day).zfill(2)) + '.json')
            file = open(filename, "w")
            file.write(result.text)
            file.close()
            current = limit

    @classmethod
    def get_data_from_file(cls, date):
        dirname = os.path.join(os.path.dirname(__file__), '../data/extracted/ree/')
        filename = os.path.join(dirname, date + '.json')
        source = open(filename, "r")
        data = json.load(source)
        source.close()
        return data
