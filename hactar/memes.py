"""Views to handle individual and collections of memes"""

from sqlalchemy.exc import IntegrityError
import flask.ext.whooshalchemy
from flask import current_app, request, session, redirect, url_for, abort, \
     render_template, flash

from hactar.models import Meme, db 

@current_app.route('/memes', methods=['GET', 'POST'])
def memes():
    """This is actually kind of the home page."""
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        uri = unicode(request.form['uri'])
        text = unicode(request.form['desc'])
        try:
            ngt = Meme(text=text, uri=uri)
            db.session.add(ngt)
            db.session.commit()
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
            filtered = Meme.query.whoosh_search(terms)
            memes = filtered.order_by(Meme.modified.desc())
            return render_template('memes.html', memes=memes,
                    add=False)
    memes = Meme.query.order_by(Meme.modified.desc())
    return render_template('memes.html', memes=memes, add=True)

@current_app.route('/memes/<int:meme>', methods=['GET', 'POST'])
def meme_handler(meme):
    """Handle any request for individual memes and defer to helper methods"""
    if request.method == 'GET':
        return get_meme(meme)
    elif 'delete' in request.form and request.form['delete'] == 'Delete':
        return delete_meme(meme)
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
    try:
        int(meme)
    except ValueError:
        abort(400)
    if not session.get('logged_in'):
        abort(401)
    current_app.logger.debug('updating meme: %s' % meme)
    text = unicode(request.form['text'])
    try:
        ngt = Meme.query.filter(Meme.id == int(meme))
        ngt.update({'text': text})
        ngt[0].update()
        db.session.commit()
        flash('Meme successfully modified')
    except ValueError as err:
        db.session.rollback()
        flash(err.message)
    return redirect(url_for('memes'))

def delete_meme(meme):
    """Remove a meme from the db."""
    if not session.get('logged_in'):
        abort(401)
    try:
        Meme.query.filter(Meme.id == int(meme)).delete()
        db.session.commit()
        flash('Meme successfully deleted')
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
