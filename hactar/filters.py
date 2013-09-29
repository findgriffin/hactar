"""Various jinja2 filters for hactar"""
import datetime
from httplib import responses

from flask import current_app

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
def _jinja2_filter_reldatetime(date):
    """Application wide datetime filter."""
    now = datetime.datetime.now()
    if type(date) == datetime.datetime:
        dtime = date
    elif type(date) in (float, int):
        dtime = datetime.datetime.fromtimestamp(date)
    else:
        return 'unknown type %s for date: %s' % (type(date), date)
    delta = now - dtime
    if delta.days > 1:
        return '%s days ago' % delta.days
    elif delta.days == 1:
        return 'yesterday'
    else:
        if delta.seconds > 7200:
            return '%s hours ago' % int(round(float(delta.seconds)/60/60))
        elif delta.seconds > 60:
            return '%s minutes ago' % int(round(float(delta.seconds)/60)) 
        elif delta.seconds > 5:
            return '%s seconds ago' % delta.seconds
        else:
            return 'just now'

@current_app.template_filter('status')
def _jinja2_filter_status(code):
    if code == 200:
        return responses[code]
    else:
        return '%s (%s)' % (responses[code], code)

