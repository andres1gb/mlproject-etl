from utils.dates import MonthString
from logging import Logger
from datetime import datetime
import requests
import os

class Extractor:
    URL = "https://www.mibgas.es/es/file-access/MIBGAS_Data_%s.xlsx?path=AGNO_%s/XLS"

    @classmethod
    def get_data(cls, start, end):
        print("Downloading Mibgas data from %s to %s" % (start, end))
        start, _ = MonthString.get_parts(start, '-')
        end, _ = MonthString.get_parts(end, '-')
        now = datetime.now()
        if start > now.year:
            raise ValueError("Start date is in the future")

        if end > now.year:
            end = now

        for year in range(start, end+1):
            url = Extractor.URL % (year, year)
            headers = {
                "accept": "*/*"
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                Logger.log(
                    "Error downloading data for year %s. Response code: %d" % (year, response.status_code))
                return False

            dirname = os.path.join(os.path.dirname(__file__), '../data/extracted/mibgas')
            filename = os.path.join(dirname, "%s" % year)+ '.xlsx'
            file = open(filename, "wb")
            file.write(response.content)
            file.close()

        
