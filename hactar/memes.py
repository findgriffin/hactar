"""Views to handle individual and collections of memes"""

from sqlalchemy.exc import IntegrityError
from flask import current_app, request, session, redirect, url_for, abort, \
     render_template, flash, jsonify, get_flashed_messages

from hactar.models import Meme, db, is_uri
from hactar.scraper import crawl
from datetime import datetime as dtime

@current_app.route('/api/memes', methods=['GET', 'POST'])
def api_memes():
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
    if request.method == 'POST':
        post_memes()
    terms = request.args.get('q')
    if terms:
        mlist = search_memes(terms)
    else:
        mlist = get_memes()
        terms = False
    return mlist, terms


@current_app.route('/memes/<int:meme>', methods=['GET', 'POST'])
def meme_handler(meme):
    """Handle any request for individual memes and defer to helper methods"""
    hdrs = request.headers
    if 'Content-Type' in hdrs and hdrs['Content-Type'] == 'application/json':
        json = True
    else:
        json = False
    if request.method == 'GET':
        first = Meme.query.filter(Meme.id == int(meme)).first_or_404()
        if json:
            return jsonify(first.dictify())
        else:
            return render_template('meme.html', meme=first)
    elif 'delete' in request.form and request.form['delete'] == 'Delete':
        return delete_meme(meme)
    elif 'status_code' in request.form or json:
        return update_content(meme)
    else:
        return update_meme(meme)
    
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
    current_app.logger.debug('looking for memes with terms: %s' % terms)
    filtered = Meme.search_query(terms)
    return filtered.order_by(Meme.modified.desc())

def get_memes():
# this produces an SAWarning when db is empty (empty sequence)
    return Meme.query.order_by(Meme.modified.desc())


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
        first.modified = dtime.now()
        db.session.commit()
        if current_app.celery_running and first.uri:
            current_app.logger.debug('submitting to celery: %s' % first)
            cookie = request.cookies.get('session')
            crawl.delay(first.id, first.uri, {'session': cookie})
        flash('Meme successfully modified')
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    return redirect(url_for('memes'))

def update_content(meme):
    """Update a memes content (for use by crawler)"""
    if not session.get('logged_in'):
        abort(401)
    try:
        current_app.logger.debug('updating content: %s' % meme)
        first = Meme.query.filter(Meme.id == int(meme)).first_or_404()
        assert 'status_code' in request.form
        for key, val in request.form.items():
            setattr(first, key, val)
        first.checked = dtime.now()
        db.session.commit()
        return jsonify({meme: True})
    except ValueError as err:
        db.session.rollback()
        flash(err.message)

def delete_meme(meme):
    """Remove a meme from the db."""
    if not session.get('logged_in'):
        abort(401)
    try:
        Meme.query.filter(Meme.id == int(meme)).delete()
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
    return redirect(url_for('memes'))
