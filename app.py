"""Put the hactar app together"""
import os

from sqlalchemy.exc import IntegrityError
from flask import Flask, redirect, session, g, url_for
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from hactar.models import db, setup

# create our little application :)
app = Flask(__name__)
db.init_app(app)

app.config.from_envvar('HACTAR_SETTINGS', silent=True)
with app.app_context():
    import hactar.errors
    import hactar.memes
    import hactar.actions
    import hactar.points
    import hactar.filters
    import hactar.login

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def home():
    return redirect(url_for('memes'))

def init_db(app):
    """ Delete the existing database and create new database from scratch."""
    import shutil
    whoosh = app.config['WHOOSH_BASE']
    try:
        shutil.rmtree(whoosh)
    except OSError:
        pass
    import os
    if os.path.exists(db_path(app)):
        os.remove(db_path(app))
    db_dir = os.path.sep.join(db_path(app).split(os.path.sep)[:-1])
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)
    with app.test_request_context():
        db.create_all()

def create_app():
    return app

def config_app(application):
    # Load default config and override config from an environment variable
    import json
    conf = json.load(open('config.json', 'rb'))['develop']
    application.config.update(conf)
    application.celery_running = False

def db_path(app):
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    return uri.replace('sqlite:///', '')

if __name__ == '__main__':
    config_app(app)
    import sys
    if sys.argv[-1] == 'clean':
        init_db(app)
        exit(0)
    elif not os.path.exists(db_path(app)):
        init_db(app)
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    app.index_service = setup('develop')
    manager.run()
