"""Various helper functions used by hactar"""
from datetime import date
import calendar

def parse_iso8601(text):
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
        last = date(year, month, days)
    elif len(parts) == 1:
        year = int(parts[0])
        first = date(year, 1, 1)
        last = date(year, 12, 31)
    else:
        raise ValueError('too many parts in iso 8601 date')

    return first, last 
