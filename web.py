# -*- coding: utf-8 -*-
"""
    Hactar Web Interface 
    ~~~~~~
    Using flask framework, based on flaskr example app by Armin Ronacher
    :license: BSD, see LICENSE for more details.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

from hactar import core

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='/tmp/hactar.db',
    DEBUG=True,
    SECRET_KEY='cricket is a stupid sport',
    USERNAME='admin',
    PASSWORD='cricket'
))
app.config.from_envvar('HACTAR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_nuggets():
    db = get_db()
    cur = db.execute('select uri, text from nuggets order by uri, text')
    nuggets = cur.fetchall()
    return render_template('show_nuggets.html', nuggets=nuggets)


@app.route('/add', methods=['POST'])
def add_nugget():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    uri = request.form['uri']
    text = request.form['desc']
    try:
        ngt = core.Nugget(text, uri)
        ngt.create_index()
        db.execute('insert into nuggets (id, uri, text, added, modified, keywords)\
                values (?, ?, ?, ?, ?, ?)', [ngt.id, ngt.uri, text, ngt.added,
                    ngt.modified, ','.join(ngt.keywords)])
        db.commit()
        flash('New nugget was successfully added')
    except ValueError as err:
        flash(err.message)
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


if __name__ == '__main__':
    init_db()
    app.run()
