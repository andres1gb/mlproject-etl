from utils.dates import MonthString
from logging import Logger
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import os
import pandas as pd


class Extractor:
    URL = "https://www.mibgas.es/es/file-access/MIBGAS_Data_%s.xlsx?path=AGNO_%s/XLS"
    cache = {} # we use a cache to avoid reading yearly files for each day

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
    
    @classmethod
    def get_data_from_file(cls, date):
        date = datetime.strptime(date, "%Y-%m-%d")
        price = Extractor.get_data_from_cache(date)
        if not price is None:
            return price
        
        dirname = os.path.join(os.path.dirname(__file__), '../data/extracted/mibgas/')
        filename = os.path.join(dirname, str(date.year) + '.xlsx')
        data = pd.read_excel(filename, sheet_name="Regulated gas")
        data = data[data["Delivery Zone"] == 'ES'] # filter out headers and Portugal rows
        for _, row in data.iterrows():
            row_date = row['Trading Day '].strftime("%Y-%m-%d")
            price = row[data.columns[4]]
            if pd.isna(price):
                # when the price is empty, gas volume used for the day is zero, so price is zero as well
                price = 0
            Extractor.cache[row_date] = price
        return Extractor.get_data_from_cache(date)

    @classmethod
    def get_data_from_cache(cls, date):
        date = date.strftime("%Y-%m-%d")
        if date in Extractor.cache:
            return Extractor.cache[date]
        else:
            return None        

class GasPrice:
    initial_date = datetime(2022,6,14) # fixed cap of 40.00 EUR/MWh
    plus_5_0 = datetime(2023,1,1) # cap increased monthly by 5.00 EUR
    plus_1_1 = datetime(2023,4,1) # cap increased montly by 1.10 EUR
    final_date = datetime(2023,12,31) # cap fixed to 65.00 EUR/MWh

    @classmethod
    def get_cap_for_date(cls, date):
        date = datetime.strptime(date, "%Y-%m-%d")
        cap = None
        if date >= GasPrice.initial_date:
            cap = 40.0
            current = datetime(GasPrice.initial_date.year, GasPrice.initial_date.month, 1) + relativedelta(months=1)
            while current <= date:
                if current >= GasPrice.plus_5_0 and current < GasPrice.plus_1_1:
                    cap += 5.0
                if current >= GasPrice.plus_1_1 and current < GasPrice.final_date:
                    cap += 1.1
                current = current + relativedelta(months=1)

        return cap
        
    @classmethod
    def get_price_applied(cls, date, price):
        cap = GasPrice.get_cap_for_date(date)
        if price is None:
            price = 0.0
        if not cap is None and cap < price:
            return cap
        else:
            return price
            