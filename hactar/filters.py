"""Various jinja2 filters for hactar"""
import datetime
from httplib import responses

from hactar.models import utcnow

from flask import current_app

YEAR  = 365.256
MONTH = YEAR/12.0

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday' , 'Thursday' , 'Friday',
'Saturday' , 'Sunday']

@current_app.template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
    """Application wide datetime filter."""
    if type(date) == datetime.datetime:
        dtime = date
    else:
        dtime = datetime.datetime.fromtimestamp(date)
    if not fmt:
        fmt = '%H:%M %d/%m/%Y'
    return dtime.strftime(fmt)

@current_app.template_filter('reldatetime')
def _jinja2_filter_reldatetime(date, now=None):
    """Application wide datetime filter. We allow passing in a different value
    of 'now' to assist # with testing"""
    if now == None:
        now = utcnow()
    if type(date) == datetime.datetime:
        dtime = date
    elif type(date) in (float, int):
        dtime = datetime.datetime.fromtimestamp(date).replace(tzinfo=pytz.utc)
    else:
        return 'unknown type %s for date: %s' % (type(date), date)
    delta = now - dtime
    if delta.total_seconds() < 0:
        mkrel = lambda s: 'in '+s
        future = True
        delta = abs(delta)
    else:
        mkrel = lambda s: s+' ago'
        future = False
        delta = abs(delta)
    if delta.days > 2*YEAR:
        return mkrel('%s years' % int(delta.days/YEAR))
    elif delta.days > 2*MONTH:
        return mkrel('%s months' % int(delta.days/MONTH))
    elif delta.days > 1:
        return mkrel('%s days' % delta.days)
    elif delta.days == 1:
        return 'tomorrow' if future else 'yesterday'
    else:
        if delta.seconds > 7200:
            return mkrel('%s hours' % int(round(float(delta.seconds)/60/60)))
        elif delta.seconds > 60:
            return mkrel('%s minutes' % int(round(float(delta.seconds)/60)))
        elif delta.seconds > 5:
            return mkrel('%s seconds' % delta.seconds)
        else:
            return 'just now'

def _form_reldatetime(main, future):
    if future:
        return 'in '+main
    else:
        return main+' ago'

@current_app.template_filter('reldate')
def _jinja2_filter_reldate(date, pretty='medium'):
    """
    Given a date object, return a human readable representation like Mon "27/9".

    @param  date    date    The date to display
    @param  string  pretty  Can be one of 'short', 'medium' (default) or 'long'.
    """
    if pretty == 'short':
        return date.strftime('%a')
    elif pretty == 'medium':
        return date.strftime('%a %e')
    elif pretty == 'long':
        return date.strftime('%A %d/%m')

@current_app.template_filter('status')
def _jinja2_filter_status(code):
    """Return human readable text for HTTP status codes"""
    if code == 200:
        return responses[code]
    elif code == -2:
        return 'Crawl Failed (-2)'
    elif code == -1:
        return 'Not checked (-1)'
    else:
        return '%s (%s)' % (responses[code], code)

