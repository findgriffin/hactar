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
def show_nuggets():
    """This is actually kind of the home page."""
    nuggets = Nugget.query.order_by(Nugget.modified.desc())
    return render_template('show_nuggets.html', nuggets=nuggets, add=True)


@app.route('/add', methods=['POST'])
def add_nugget():
    """Add a nugget to the database. (by handling a POST request)"""
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

@app.route('/find', methods=['POST'])
def find_nugget():
    """Search for nuggets."""
    terms = request.form['q']
    try:
        term = terms.split()[0]
    except IndexError:
        term = ''
    app.logger.debug('looking for search term: %s' % term)
    filtered = Nugget.query.filter(Nugget.keywords.like('%%%s%%' % term))
    nuggets = filtered.order_by(Nugget.modified.desc())
    return render_template('show_nuggets.html', nuggets=nuggets, add=False)

@app.route('/edit/<int:nugget>', methods=['GET'])
def edit_nugget(nugget):
    """Edit (or delete) a nugget."""
    nuggets = Nugget.query.filter(Nugget.id == int(nugget)).all()
    if not nuggets:
        abort(404)
    app.logger.debug('found: %s' % nuggets)
    return render_template('edit_nugget.html', nugget=nuggets[0])

@app.route('/update/<int:nugget>', methods=['GET', 'POST'])
def update_nugget(nugget):
    """Update a nugget (i.e. implement an edit to a nugget)"""
    try:
        int(nugget)
    except ValueError:
        abort(400)
    if not session.get('logged_in'):
        abort(401)
    app.logger.debug('updating nugget: %s' % nugget)
    text = request.form['text']
    try:
        ngt = Nugget.query.filter(Nugget.id == int(nugget))
        ngt.update({'text': text})
        ngt[0].update()
        db.session.commit()
        flash('Nugget successfully modified')
    except ValueError as err:
        flash(err.message)
    except IntegrityError as err:
        if 'primary key must be unique' in err.message.lower():
            flash('Nugget with that URI or description already exists')
    return redirect(url_for('show_nuggets'))

@app.route('/delete/<int:nugget>', methods=['GET', 'POST'])
def delete_nugget(nugget):
    """Remove a nugget from the db."""
    try:
        int(nugget)
    except ValueError:
        abort(400)
    if not session.get('logged_in'):
        abort(401)
    app.logger.debug('deleting nugget: %s' % nugget)
    try:
        ngt = Nugget.query.filter(Nugget.id == int(nugget)).delete()
#       ngt.create()
        db.session.commit()
        flash('Nugget successfully deleted')
    except ValueError as err:
        flash(err.message)
    except IntegrityError as err:
        if 'primary key must be unique' in err.message.lower():
            flash('Nugget with that URI or description already exists')
    return redirect(url_for('show_nuggets'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle logins."""
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
    """Handle logging out."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_nuggets'))

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


if __name__ == '__main__':
    try:
        open(app.config['SQLALCHEMY_DATABASE_URI'], 'rb')
    except IOError:
        with app.test_request_context():
            db.create_all()
    app.run()
