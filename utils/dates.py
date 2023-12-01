import datetime
import calendar

MIN_YEAR_ALLOWED = 2000
DEFAULT_SEPARATOR = '-'


class MonthString(datetime.datetime):

    @staticmethod
    def from_date(date: datetime.datetime, sep=DEFAULT_SEPARATOR):
        return "%d%s%s" % (date.year, sep, str(date.month).zfill(2))

    @staticmethod
    def get_parts(date: str, sep=DEFAULT_SEPARATOR):
        if not MonthString.is_valid(date, sep):
            raise ValueError("Bad date format")

        parts = date.split(sep)
        return int(parts[0]),  int(parts[1])

    @staticmethod
    def is_valid(date: str, sep=DEFAULT_SEPARATOR):
        parts = date.split(sep)
        if len(parts) != 2:
            return False

        year = int(parts[0])
        month = int(parts[1])
        if year < MIN_YEAR_ALLOWED or year > datetime.datetime.now().year:
            return False

        if month < 1 or month > 12:
            return False

        return True

    @staticmethod
    def to_datetime(date: str, sep=DEFAULT_SEPARATOR):
        year, month = MonthString.get_parts(date, sep)
        return datetime.datetime(year, month, 1)

    @staticmethod
    def first_day(date: str, sep=DEFAULT_SEPARATOR):
        year, month = MonthString.get_parts(date, sep)
        return datetime.datetime(year, month, 1, 0, 0, 0)

    @staticmethod
    def last_day(date: str, sep=DEFAULT_SEPARATOR):
        year, month = MonthString.get_parts(date, sep)
        month_range = calendar.monthrange(year, month)
        last_day = month_range[1]
        return datetime.datetime(year, month, last_day, 23, 59, 59)
