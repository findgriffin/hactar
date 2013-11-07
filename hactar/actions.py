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

@current_app.route('/api/actions', methods=['GET', 'POST'])
def api_actions():
    """Handle requests for actions through the api"""
    mlist, terms = actions_handler()
    resp = {'actions': [], 'flashes': []}
    [resp['actions'].append(action.dictify()) for action in mlist]
    resp['flashes'] = get_flashed_messages()
    return jsonify(resp) 

@current_app.route('/actions', methods=['GET', 'POST'])
def actions(json=False):
    """Handle requests for actions and defer to helper methods"""
    mlist, terms = actions_handler()
    week = last_weeks_points()
    if json:
        resp = {'actions': []}
        [resp['actions'].append(action.dictify()) for action in mlist]
        return jsonify(resp)
    else:
        return render_template('actions.html', actions=mlist, searched=terms,
                week=week)

def actions_handler():
    """Call the various helper methods, be used by api and html"""
    if request.method == 'POST':
        post_actions()
    terms = request.args.get('q')
    finish = request.args.get('finish')
    if terms:
        current_app.logger.debug('looking for memes with terms: %s' % terms)
        query = Action.search_query(terms)
    else:
        # this produces an SAWarning when db is empty (empty sequence)
        query = Action.query
        terms = False
    if finish:
        f_start, f_end = parse_iso8601(finish)
        current_app.logger.debug('getting actions finished between %s and %s' % (f_start, f_end))
        query = query.filter(Action.finish_time.between(f_start, f_end))
    query = query.order_by(Action.modified.desc())
    if not terms and not finish:
        query = query.limit(10)
    return query, terms


@current_app.route('/api/actions/<int:action>', methods=['GET', 'POST', 'DELETE'])
def api_action(action):
    """Handle action requests through the api"""
    if request.method == 'GET':
        first = get_action(action)
        return jsonify(first.dictify())
    elif request.method == 'DELETE':
        delete_action(action)

        return jsonify({action: u'deleted', 'flashes': get_flashed_messages()})
    else:
        updated = update_content(action)
        resp = {action: updated.dictify(), 'flashes': get_flashed_messages()}
        return jsonify(resp)


@current_app.route('/actions/<int:action>', methods=['GET', 'POST'])
def action_handler(action):
    """Handle any request for individual actions and defer to helper methods"""
    hdrs = request.headers
    if 'Content-Type' in hdrs and hdrs['Content-Type'] == 'application/json':
        json = True
    else:
        json = False
    if request.method == 'GET':
        first = get_action(action)
        if json:
            return jsonify(first.dictify())
        else:
            return render_template('action.html', action=first)
    elif 'delete' in request.form and request.form['delete'] == 'Delete':
        delete_action(action)
        return redirect(url_for('actions'))
    elif 'status_code' in request.form or json:
        return update_content(action)
    else:
        update_action(action)
        return redirect(url_for('actions'))

def get_action(action_id):
    """Return either the action given by action_id or raise a 404""" 
    return Action.query.filter(Action.id == int(action_id)).first_or_404()
    
def post_actions():
    """This is actually kind of the home page."""
    if not session.get('logged_in'):
        abort(401)
    newargs = {}
    form = request.form
    def parse_date_field(name):
        try:
            if len(form[name]) < 3:
                raise KeyError # dont give to parser if it's not a datetime
            newargs[name] = parse(form[name], dayfirst=DAYFIRST)
        except ValueError:
            flash('Unable to parse %s date: %s' % (name, form[name]))
        except KeyError as err:
            current_app.logger.debug(err.message)
            pass
    newargs['text'] = unicode(form['what'])
    parse_date_field('due')
    parse_date_field('start')
    parse_date_field('finish')
    if 'points' in form:
        newargs['points'] = int(form['points'])
    if 'just_finished' in form and 'finish' not in newargs:
        newargs['finish'] = dtime.now()
    try:
        newaction = Action(**newargs)
        db.session.add(newaction)
        db.session.commit()
        flash('New action was successfully added')
    except ValueError as err:
        current_app.logger.debug('got error: %s' % err.message)
        db.session.rollback()
        flash(err.message)
    except IntegrityError as err:
        db.session.rollback()
        if 'primary key must be unique' in err.message.lower():
            current_app.logger.debug("can't add duplicate action: %s" % uri )
            flash('action with that URI or description already exists')
        else:
            abort(500)

def update_action(action):
    """Update a action (i.e. implement an edit to a action)"""
    if not session.get('logged_in'):
        abort(401)
    current_app.logger.debug('updating action: %s' % action)
    current_app.logger.debug('session: %s' % session.items())
    text = unicode(request.form['what'])
    try:
        first = Action.query.filter(Action.id == int(action)).first_or_404()
        first.text = text
        first.modified = dtime.now()
        db.session.commit()
        flash('action successfully modified')
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    return first

def update_content(action):
    """Update a actions content (for use by crawler)"""
    form = request.form
    if not session.get('logged_in'):
        abort(401)
    try:
        current_app.logger.debug('updating content: %s' % action)
        first = Action.query.filter(Action.id == int(action)).first_or_404()
        if 'status_code' in form:
            first.checked = dtime.now()
            for key, val in form.items():
                setattr(first, key, val)
        elif 'why' in form:
            first.modified = dtime.now()
            first.text = unicode(form['why'])
        else:
            abort(400)
        db.session.commit()
        flash('action successfully modified')
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    return first

def delete_action(action):
    """Remove a action from the db."""
    if not session.get('logged_in'):
        abort(401)
    try:
        query = Action.query.filter(Action.id == int(action))
        query.first_or_404()
        query.delete()
        db.session.commit()
        flash('action deleted')
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    except IntegrityError as err:
        db.session.rollback()
        if 'primary key must be unique' in err.message.lower():
            flash('action with that URI or description already exists')
        else:
            abort(500)

def last_weeks_points(today=None):
    """Returns today's points and the last 7 days (i.e. 8 days total)"""
    if today is None:
        today = dtime.now().date()
    week = []
    for i in xrange(8):
        day = today-tdelta(days=i)
        week.append((day, get_daily_points(day)))
    return week
    
def get_daily_points(day):
    completed = Action.query.filter(Action.finish_date == day).all()
    return sum([item.points for item in completed])

