"""Views to handle individual and collections of memes"""

from sqlalchemy.exc import IntegrityError
from flask import current_app, request, session, redirect, url_for, abort, \
     render_template, flash, jsonify

from hactar.models import Meme, db 
from hactar.scraper import crawl
from datetime import datetime as dtime

@current_app.route('/memes', methods=['GET', 'POST'])
def memes():
    """This is actually kind of the home page."""
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        uri = unicode(request.form['uri'])
        text = unicode(request.form['desc'])
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
    else:
        terms = request.args.get('q')
        if terms:
            import pdb; pdb.set_trace()
            current_app.logger.debug('looking for memes with terms: %s' % terms)
            filtered = Meme.search_query(terms)
            memes = filtered.order_by(Meme.modified.desc())
            return render_template('memes.html', memes=memes,
                    add=False)
    # this produces an SAWarning when db is empty (empty sequence)
    memes = Meme.query.order_by(Meme.modified.desc())
    return render_template('memes.html', memes=memes, add=True)

@current_app.route('/memes/<int:meme>', methods=['GET', 'POST'])
def meme_handler(meme):
    """Handle any request for individual memes and defer to helper methods"""
    if request.method == 'GET':
        return get_meme(meme)
    elif 'delete' in request.form and request.form['delete'] == 'Delete':
        return delete_meme(meme)
    elif 'status_code' in request.form:
        return update_content(meme)
    else:
        return update_meme(meme)


def get_meme(meme):
    """Edit (or delete) a meme."""
    memes = Meme.query.filter(Meme.id == int(meme)).all()
    if not memes:
        abort(404)
    return render_template('meme.html', meme=memes[0])

def update_meme(meme):
    """Update a meme (i.e. implement an edit to a meme)"""
    if not session.get('logged_in'):
        abort(401)
    current_app.logger.debug('updating meme: %s' % meme)
    current_app.logger.debug('session: %s' % session.items())
    text = unicode(request.form['text'])
    try:
        result = Meme.query.filter(Meme.id == int(meme))
        first = result.first_or_404()
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
        result = Meme.query.filter(Meme.id == int(meme))
        first = result.first_or_404()
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
