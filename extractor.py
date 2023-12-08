import datetime
import argparse
from sources import aemet, ree, mibgas
from utils.logger import Logger
from utils.dates import MonthString

DEFAULT_MONTH_FROM = "2019-01"


def parse_args():
    parser = argparse.ArgumentParser(
        prog='extractor.py',
        description='Loads data from Aemet, REE and other sources',
        epilog='Created by Andrés Purriños 2023'
    )
    current_month = MonthString.from_date(datetime.datetime.now())
    parser.add_argument('-ds', choices=['aemet', 'ree'], help='Data source to download')
    parser.add_argument('-f', default=DEFAULT_MONTH_FROM, help='First month to download (YYYY-MM format)')
    parser.add_argument('-t', default=current_month, help='Last month to download (YYYY-MM format)')
    return vars(parser.parse_args())


if __name__ == '__main__':    
    args = parse_args()

    source = args['ds']
    start = args['f']
    end = args['t']

    source = "mibgas"

    if not MonthString.is_valid(start):
        Logger.log("Starting month is not valid: %s" % start)

    if not MonthString.is_valid(end):
        Logger.log("Ending month is not valid: %s" % end)

    match source:
        case "aemet":
            aemet.Extractor.get_data(start, end)
        case "ree":
            ree.Extractor.get_data(start, end)
        case "mibgas":
            mibgas.Extractor.get_data(start, end)
        case None:
            aemet.Extractor.get_data(start, end)
            ree.Extractor.get_data(start, end)
            mibgas.Extractor.get_data(start, end)

