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
    json = request.headers['Content-Type'] == 'application/json'
    if request.method == 'GET':
        first = Meme.query.filter(Meme.id == int(meme)).first_or_404()
        if json:
            return jsonify(first.dictify())
        else:
            return render_template('meme.html', meme=first)
    elif 'delete' in request.form and request.form['delete'] == 'Delete':
        return delete_meme(meme)
    else:
        updated = update_meme(meme)
        if json:
            return jsonify(updated.dictify())
        else:
            return redirect(url_for('memes'))


def update_meme(meme):
    """Update a meme (i.e. implement an edit to a meme)"""
    if not session.get('logged_in'):
        abort(401)
    current_app.logger.debug('updating meme: %s' % meme)
    current_app.logger.debug('session: %s' % session.items())
    form = request.form
    try:
        first = Meme.query.filter(Meme.id == int(meme)).first_or_404()
        checked = 'status_code' in request.form
        if checked: 
            first.checked = dtime.now()
        if 'text' in form:
            text = unicode(request.form['text'])
            if first.text != text:
                first.text = text
                first.modified = dtime.now()
        for key, val in form.items():
            setattr(first, key, val)
        flash('Meme successfully modified')
        db.session.commit()
        # really important to not create infinite loop with celery
        # celery must not post without status code
        if current_app.celery_running and first.uri and not checked:
            current_app.logger.debug('submitting to celery: %s' % first)
            cookie = request.cookies.get('session')
            crawl.delay(first.id, first.uri, {'session': cookie})
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    return first


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
