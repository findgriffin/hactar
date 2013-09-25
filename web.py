# -*- coding: utf-8 -*-
"""
    Hactar Web Interface 
    ~~~~~~
    Using flask framework, based on flaskr example app by Armin Ronacher
    :license: BSD, see LICENSE for more details.
"""
import datetime
from sqlalchemy.exc import IntegrityError
import flask.ext.whooshalchemy
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from models import Meme, db 

# create our little application :)
app = Flask(__name__)
db.init_app(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:////tmp/hactar.db',
    WHOOSH_BASE='/tmp/hactar_whoosh',
    DEBUG=True,
    SECRET_KEY='cricket is a stupid sport',
    USERNAME='admin',
    PASSWORD='cricket'
))
app.config.from_envvar('HACTAR_SETTINGS', silent=True)

@app.errorhandler(404)
def not_found(exc):
    """Handle HTTP not found error."""
    return render_template('error.html', exc=exc), 404

@app.errorhandler(500)
def internal_server_error(exc):
    """Handle internal server error."""
    return render_template('error.html', exc=exc), 500

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def home():
    return redirect(url_for('memes'))

@app.route('/memes', methods=['GET', 'POST'])
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
            db.session.rollback()
            flash(err.message)
        except IntegrityError as err:
            db.session.rollback()
            if 'primary key must be unique' in err.message.lower():
                flash('Meme with that URI or description already exists')
    else:
        terms = request.args.get('q')
        if terms:
            app.logger.debug('looking for memes with terms: %s' % terms)
            filtered = Meme.query.whoosh_search(terms)
            memes = filtered.order_by(Meme.modified.desc())
            return render_template('memes.html', memes=memes,
                    add=False)
    memes = Meme.query.order_by(Meme.modified.desc())
    return render_template('memes.html', memes=memes, add=True)

@app.route('/memes/<int:meme>', methods=['GET', 'POST'])
def meme(meme):
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
    app.logger.debug('updating meme: %s' % meme)
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
    try:
        int(meme)
    except ValueError:
        abort(400)
    if not session.get('logged_in'):
        abort(401)
    try:
        Meme.query.filter(Meme.id == int(meme)).delete()
        db.session.commit()
        flash('Meme successfully deleted')
    except ValueError as err:
        flash(err.message)
    except IntegrityError as err:
        if 'primary key must be unique' in err.message.lower():
            flash('Meme with that URI or description already exists')
    return redirect(url_for('memes'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle logins."""
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            flash('Invalid username')
        elif request.form['password'] != app.config['PASSWORD']:
            flash('Invalid password')
        else:
            session['logged_in'] = True
            flash('You were logged in')
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    """Handle logging out."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))

@app.template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
    """Application wide datetime filter."""
    if type(date) == datetime.datetime:
        dtime = date
    else:
        dtime = datetime.datetime.fromtimestamp(date)
    if not fmt:
        fmt = '%H:%M %d/%m/%Y'
    return dtime.strftime(fmt)


def init_db():
    """ Delete the existing database and create new database from scratch."""
    db_path = app.config['SQLALCHEMY_DATABASE_URI']
    import os
    if os.path.exists(db_path):
        os.remove(db_path)
    with app.test_request_context():
        db.create_all()

def create_app():
    return app



if __name__ == '__main__':
    try:
        open(app.config['SQLALCHEMY_DATABASE_URI'], 'rb')
    except IOError:
        with app.test_request_context():
            db.create_all()
    app.run()
