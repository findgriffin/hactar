"""Various helper functions used by hactar"""
from datetime import date

def parse_iso8601(text):
    """Parse an iso 8601 string, must be in extended format, currently only
    supports dates."""
    parts = text.split('-')
    if len(parts) < 1:
        raise ValueError('date %s is invalid')
    else:
        year = int(parts[0])
        accuracy = 'year'
    if len(parts) > 1:
        month = int(parts[1])
        accuracy = 'month'
    else:
        month = 1
    if len(parts) > 2:
        day = int(parts[2])
        accuracy = 'day'
    else:
        day = 1
    return date(year, month, day), accuracy
