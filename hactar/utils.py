"""Various helper functions used by hactar"""
from datetime import date
from datetime import timedelta as tdelta
from datetime import datetime as dtime
import calendar
import pytz

def parse_iso8601(text, tz=None):
    """Parse an iso 8601 string, must be in extended format, currently only
    supports dates."""
    parts = text.split('-')
    if len(parts) < 1:
        raise ValueError('date %s is invalid')
    elif len(parts) == 3:
        first = date(int(parts[0]), int(parts[1]), int(parts[2]))
        last = first
    elif len(parts) == 2:
        year = int(parts[0])
        month = int(parts[1])
        first = date(year, month, 1)
        days = calendar.monthrange(year, month)[1]
        last = first + tdelta(days-1)
    elif len(parts) == 1:
        year = int(parts[0])
        first = date(year, 1, 1)
        last = date(year, 12, 31)
    else:
        raise ValueError('too many parts in iso 8601 date')
    first = dtime(first.year, first.month, first.day, 0, 0, 0, 0, tzinfo=tz)
    last = dtime(last.year, last.month, last.day, 23, 59, 59, 999999, tzinfo=tz)

    return first, last 

def utcnow():
    return dtime.utcnow().replace(tzinfo=pytz.utc)
