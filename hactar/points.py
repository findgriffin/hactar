"""Views to handle individual and collections of actions"""

from datetime import datetime as dtime
from datetime import timedelta as tdelta
from dateutil.parser import parse

from sqlalchemy.exc import IntegrityError
from flask import current_app, request, session, redirect, url_for, abort, \
     render_template, flash, jsonify, get_flashed_messages

from hactar.models import Action, db
from hactar.utils import parse_iso8601

DAYFIRST = True

@current_app.route('/api/points', methods=['GET'])
def api_points():
    """Handle requests for points through the api"""
    mlist, terms = points_handler()
    resp = {'days': []}
    return jsonify(resp)

@current_app.route('/api/points/<date>', methods=['GET'])
def get_points(date):
    """Call the various helper methods, be used by api and html"""
        # this produces an SAWarning when db is empty (empty sequence)
    query = Action.query
    f_start, f_end = parse_iso8601(date)
    completed = query.filter(Action.finish_time.between(f_start, f_end))
    resp = {'start': f_start.strftime('%Y-%m-%d'),
            'end': f_end.strftime('%Y-%m-%d')}
    resp['points'] = sum([item.points for item in completed])
    return jsonify(resp)


def last_weeks_points(today=None):
    """Returns today's points and the last 7 days (i.e. 8 days total)"""
    if today is None:
        today = dtime.now().date()
    week = []
    for i in xrange(8):
        day = today-tdelta(days=i)
        week.append((day, get_daily_points(day)))
    return week
