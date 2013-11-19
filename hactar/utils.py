"""Various helper functions used by hactar"""
from datetime import date
from datetime import time
from datetime import timedelta as tdelta
from datetime import datetime as dtime
import calendar

def parse_iso8601(text):
    """Parse an iso 8601 string, must be in extended format, currently only
    supports dates."""
    date_text = text.split('T')[0]
    try:
        time_text = text.split('T')[1]
    except IndexError:
        time_text = None
    date_parts = date_text.split('-')
    if len(date_parts) < 1:
        raise ValueError('date %s is invalid')
    elif len(date_parts) == 3:
        first_day = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        last_day = first_day+tdelta(days=1)
    elif len(date_parts) == 2:
        year = int(date_parts[0])
        month = int(date_parts[1])
        first_day = date(year, month, 1)
        days = calendar.monthrange(year, month)[1]
        last_day = first_day + tdelta(days)
    elif len(date_parts) == 1:
        year = int(date_parts[0])
        first_day = date(year, 1, 1)
        last_day = date(year+1, 1, 1)
    else:
        raise ValueError('too many date_parts in iso 8601 date')
    if time_text:
        raise NotImplementedError('can only parse dates at this time')
    else:
        first_time = last_time = time(0, 0, 0)
    return combine_dt(first_day, first_time), combine_dt(last_day, last_time)

def combine_dt(date, time):
    return dtime(date.year, date.month, date.day, time.hour, time.minute,
            time.second)
