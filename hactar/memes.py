"""Views to handle individual and collections of memes"""
from datetime import datetime as dtime

from sqlalchemy.exc import IntegrityError
from flask import current_app, request, session, redirect, url_for, abort, \
     render_template, flash, jsonify, get_flashed_messages

from hactar.utils import utcnow
from hactar.models import Meme, db
from hactar.scraper import crawl

@current_app.route('/api/memes', methods=['GET', 'POST'])
def api_memes():
    """Handle requests for memes through the api"""
    mlist, terms = memes_handler()
    resp = {'memes': [], 'flashes': []}
    [resp['memes'].append(meme.dictify()) for meme in mlist]
    resp['flashes'] = get_flashed_messages()
    return jsonify(resp) 
@current_app.route('/memes', methods=['GET', 'POST'])
def memes(json=False):
    """Handle requests for memes and defer to helper methods"""
    mlist, terms = memes_handler()
    if json:
        resp = {'memes': []}
        [resp['memes'].append(meme.dictify()) for meme in mlist]
        return jsonify(resp)
    else:
        return render_template('memes.html', memes=mlist, searched=terms)

def memes_handler():
    """Call the various helper methods, be used by api and html"""
    if request.method == 'POST':
        post_memes()
    terms = request.args.get('q')
    if terms:
        mlist = search_memes(terms)
    else:
        mlist = get_memes()
        terms = False
    return mlist, terms


@current_app.route('/api/memes/<int:meme>', methods=['GET', 'POST', 'DELETE'])
def api_meme(meme):
    """Handle meme requests through the api"""
    if request.method == 'GET':
        first = get_meme(meme)
        return jsonify(first.dictify())
    elif request.method == 'DELETE':
        delete_meme(meme)

        return jsonify({meme: u'deleted', 'flashes': get_flashed_messages()})
    else:
        updated = update_content(meme)
        resp = {meme: updated.dictify(), 'flashes': get_flashed_messages()}
        return jsonify(resp)


@current_app.route('/memes/<int:meme>', methods=['GET', 'POST'])
def meme_handler(meme):
    """Handle any request for individual memes and defer to helper methods"""
    hdrs = request.headers
    if 'Content-Type' in hdrs and hdrs['Content-Type'] == 'application/json':
        json = True
    else:
        json = False
    if request.method == 'GET':
        first = get_meme(meme)
        if json:
            return jsonify(first.dictify())
        else:
            return render_template('meme.html', meme=first)
    elif 'delete' in request.form and request.form['delete'] == 'Delete':
        delete_meme(meme)
        return redirect(url_for('memes'))
    elif 'status_code' in request.form or json:
        return update_content(meme)
    else:
        update_meme(meme)
        return redirect(url_for('memes'))

def get_meme(meme_id):
    """Return either the meme given by meme_id or raise a 404""" 
    return Meme.query.filter(Meme.id == int(meme_id)).first_or_404()
    
def post_memes():
    """This is actually kind of the home page."""
    if not session.get('logged_in'):
        abort(401)
    uri = unicode(request.form['what'])
    text = unicode(request.form['why'])
    try:
        newmeme = Meme(text=text, uri=uri)
        db.session.add(newmeme)
        db.session.commit()
        if current_app.celery_running and newmeme.uri:
            current_app.logger.debug('submitting to celery: %s' % newmeme)
            cookie = request.cookies.get('session')
            crawl.delay(newmeme.id, newmeme.uri, {'session': cookie})
        flash('New meme was successfully added')
    except ValueError as err:
        current_app.logger.error('got error: %s' % err.message)
        db.session.rollback()
        flash(err.message)
    except IntegrityError as err:
        db.session.rollback()
        if 'primary key must be unique' in err.message.lower():
            current_app.logger.debug("can't add duplicate meme: %s" % uri )
            flash('Meme with that URI or description already exists')
        else:
            abort(500)

def search_memes(terms):
    """Return a query with the memes containing terms"""
    current_app.logger.debug('looking for memes with terms: %s' % terms)
    filtered = Meme.search_query(terms)
    return filtered.order_by(Meme.modified.desc())

def get_memes():
    """Get the latest memes"""
# this produces an SAWarning when db is empty (empty sequence)
    return Meme.query.order_by(Meme.modified.desc()).limit(10)


def update_meme(meme):
    """Update a meme (i.e. implement an edit to a meme)"""
    if not session.get('logged_in'):
        abort(401)
    current_app.logger.debug('updating meme: %s' % meme)
    current_app.logger.debug('session: %s' % session.items())
    text = unicode(request.form['why'])
    try:
        first = Meme.query.filter(Meme.id == int(meme)).first_or_404()
        first.text = text
        first.modified = utcnow()
        db.session.commit()
        if current_app.celery_running and first.uri:
            current_app.logger.debug('submitting to celery: %s' % first)
            cookie = request.cookies.get('session')
            crawl.delay(first.id, first.uri, {'session': cookie})
        flash('Meme successfully modified')
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    return first

def update_content(meme):
    """Update a memes content (for use by crawler)"""
    form = request.form
    if not session.get('logged_in'):
        abort(401)
    try:
        current_app.logger.debug('updating content: %s' % meme)
        first = Meme.query.filter(Meme.id == int(meme)).first_or_404()
        if 'status_code' in form:
            first.checked = utcnow()
            for key, val in form.items():
                setattr(first, key, val)
        elif 'why' in form:
            first.modified = utcnow()
            first.text = unicode(form['why'])
        else:
            abort(400)
        db.session.commit()
        flash('Meme successfully modified')
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    return first

def delete_meme(meme):
    """Remove a meme from the db."""
    if not session.get('logged_in'):
        abort(401)
    try:
        query = Meme.query.filter(Meme.id == int(meme))
        query.first_or_404()
        query.delete()
        db.session.commit()
        flash('Meme deleted')
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    except IntegrityError as err:
        db.session.rollback()
        if 'primary key must be unique' in err.message.lower():
            flash('Meme with that URI or description already exists')
        else:
            abort(500)
