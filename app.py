"""Put the hactar app together"""

from sqlalchemy.exc import IntegrityError
from flask import Flask, redirect, session, g, url_for
from hactar.models import db

# create our little application :)
app = Flask(__name__)
db.init_app(app)

app.config.from_envvar('HACTAR_SETTINGS', silent=True)
with app.app_context():
    import hactar.errors
    import hactar.memes
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
    import json
    conf = json.load(open('config.json', 'rb'))['develop']
    application.config.update(conf)

if __name__ == '__main__':
    config_app(app)
    try:
        open(app.config['SQLALCHEMY_DATABASE_URI'], 'rb')
    except IOError:
        with app.test_request_context():
            db.create_all()
    app.run()
