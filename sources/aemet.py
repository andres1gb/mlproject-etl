import os
import datetime
import json
from dateutil.relativedelta import relativedelta
import requests
from utils.dates import MonthString

from utils.logger import Logger


class Extractor:
    API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbmRyZXMxZ2JAZ21haWwuY29tIiwianRpIjoiYmI3ZjhkNzQtY2RjZi00YjFlLThiYjgtM2IxMzgzY2YwYjQ4IiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2OTg4MzQ5MzAsInVzZXJJZCI6ImJiN2Y4ZDc0LWNkY2YtNGIxZS04YmI4LTNiMTM4M2NmMGI0OCIsInJvbGUiOiIifQ.ERuFfi1NAE7FUbligt769f2a-7EcwBBejr2gm_uqq4k"
    URL = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/%s/fechafin/%s/todasestaciones"

    @classmethod
    def get_data(cls, start, end):
        current = MonthString.to_datetime(start)
        end = MonthString.to_datetime(end)

        while current <= end:
            cls.get_data_for_month(current.year, current.month)
            current = current + relativedelta(months=1)

    @classmethod
    def get_data_for_month(cls, year: int, month: int):
        now = datetime.datetime.now()
        start = datetime.datetime(year, month, 1)

        if start > now:
            Logger.log("Start date %s is in the future, month skipped" % start)
            return False

        end = MonthString.last_day(str(year) + '-' + str(month), '-')
        if end > now:  # limit the query to current day
            end = datetime.datetime(year, month, now.day)

        start_date = start.strftime("%Y-%m-%dT00:00:00UTC")
        end_date = end.strftime("%Y-%m-%dT23:59:59UTC")

        url = cls.URL % (start_date, end_date)
        headers = {
            "accept": "application/json",
            "api_key": cls.API_KEY
        }
        result = requests.get(url, headers=headers)

        if result.status_code != 200:
            Logger.log(
                "Error requesting data for month %s/%s. Response code: %d" % (year, month, result.status_code))
            return False
        response = result.json()

        if response['descripcion'] != 'exito':
            Logger.log("Error requesting data for month %s/%s. Response: %s" % (year, month, response))
            return False

        url = response['datos']
        result = requests.get(url, headers=headers)

        if result.status_code != 200:
            Logger.log(
                "Error downloading data for month %s/%s. Response code: %d" % (year, month, result.status_code))
            return False

        dirname = os.path.join(os.path.dirname(__file__), '../data/extracted/aemet/')
        filename = os.path.join(dirname, MonthString.from_date(start, '') + '.json')
        file = open(filename, "w")
        file.write(result.text)
        file.close()

        return True

    @classmethod
    def get_data_for_year(cls, year: int):
        for month in range(0, 12):
            cls.get_data_for_month(year, month + 1)

    @classmethod
    def get_data_from_file(cls, date):
        dirname = os.path.join(os.path.dirname(__file__), '../data/extracted/aemet/')
        filename = os.path.join(dirname, MonthString.from_date(date, '') + '.json')
        source = open(filename, "r")
        data = json.load(source)
        source.close()
        return data
