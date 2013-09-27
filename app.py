# -*- coding: utf-8 -*-
"""
    Hactar Web Interface 
    ~~~~~~
    Using flask framework, based on flaskr example app by Armin Ronacher
    :license: BSD, see LICENSE for more details.
"""
import datetime
import traceback

from sqlalchemy.exc import IntegrityError
import flask.ext.whooshalchemy
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from hactar.models import Meme, db 

# create our little application :)
app = Flask(__name__)
db.init_app(app)

app.config.from_envvar('HACTAR_SETTINGS', silent=True)
with app.app_context():
    import errors
    import hactar.memes

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def home():
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

@app.template_filter('reldatetime')
def _jinja2_filter_reldatetime(date):
    """Application wide datetime filter."""
    now = datetime.datetime.now()
    if type(date) == datetime.datetime:
        dtime = date
    else:
        dtime = datetime.datetime.fromtimestamp(date)
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


def config_app(application):
    # Load default config and override config from an environment variable
    application.config.update(dict(
        SQLALCHEMY_DATABASE_URI='sqlite:////tmp/hactar/hactar.db',
        WHOOSH_BASE='/tmp/hactar/whoosh',
        DEBUG=True,
        SECRET_KEY='cricket is a stupid sport',
        USERNAME='admin',
        PASSWORD='cricket'
    ))

if __name__ == '__main__':
    config_app(app)
    try:
        open(app.config['SQLALCHEMY_DATABASE_URI'], 'rb')
    except IOError:
        with app.test_request_context():
            db.create_all()
    app.run()
