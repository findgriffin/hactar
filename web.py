# -*- coding: utf-8 -*-
"""
    Hactar Web Interface 
    ~~~~~~
    Using flask framework, based on flaskr example app by Armin Ronacher
    :license: BSD, see LICENSE for more details.
"""
import datetime
from sqlalchemy.exc import IntegrityError
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from models import Nugget, db


# create our little application :)
app = Flask(__name__)
db.init_app(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:////tmp/hactar.db',
    DEBUG=True,
    SECRET_KEY='cricket is a stupid sport',
    USERNAME='admin',
    PASSWORD='cricket'
))
app.config.from_envvar('HACTAR_SETTINGS', silent=True)


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_nuggets():
    nuggets = Nugget.query.all() # can filter or pageinate
    return render_template('show_nuggets.html', nuggets=nuggets)


@app.route('/add', methods=['POST'])
def add_nugget():
    if not session.get('logged_in'):
        abort(401)
    uri = request.form['uri']
    text = request.form['desc']
    try:
        ngt = Nugget(text=text, uri=uri)
#       ngt.create()
        db.session.add(ngt)
        db.session.commit()
        flash('New nugget was successfully added')
    except ValueError as err:
        flash(err.message)
    except IntegrityError as err:
        if 'primary key must be unique' in err.message.lower():
            flash('Nugget with that URI or description already exists')
    return redirect(url_for('show_nuggets'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_nuggets'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_nuggets'))

@app.template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
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


if __name__ == '__main__':
    try:
        open(app.config['SQLALCHEMY_DATABASE_URI'], 'rb')
    except IOError:
        with app.test_request_context():
            db.create_all()
    app.run()
