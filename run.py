#! /usr/bin/env python
import logging
import os
import sys
from json import load

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import app, config_app

# apparently importing whooshalchemy and Meme is required to make whooshalchemy
# work, this seems like too much magic
import flask.ext.whooshalchemy
from hactar.models import Meme, db


def main(test=False):
    """Start tornado running hactar."""
    conf = load(open('config.json', 'rb'))
    if test:
        config_app(app)
    else:
        secrets = load(open(conf['SECRETS'], 'rb'))
        conf['USERNAME'] = secrets['hactar']['username']
        conf['PASSWORD'] = secrets['hactar']['password']
        conf['SECRET_KEY'] = secrets['installed']['client_secret']
        app.config.update(conf)

    
    logpath = os.path.join(conf['LOG_DIR'], conf['LOG_MAIN'])
    handler = logging.handlers.RotatingFileHandler(logpath, maxBytes=100000,
            backupCount=4)
    fmtr = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(fmtr)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    with app.app_context():
        db.init_app(app)
    if not os.path.exists(conf['SQLALCHEMY_DATABASE_URI'].lstrip('sqlite:///')):
        with app.test_request_context():
            db.create_all()
    app.logger.debug('starting app with config: %s' % app.config)
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8080)
    IOLoop.instance().start()


if __name__ == "__main__":
    if sys.argv[-1] == 'test':
        main(True)
    main()
