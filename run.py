#! /usr/bin/env python
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from json import load

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import app

# apparently importing whooshalchemy and Meme is required to make whooshalchemy
# work, this seems like too much magic
import flask.ext.whooshalchemy
from hactar.models import Meme, db


def main(test=False):
    """Start tornado running hactar."""
    conf = load(open('config.json', 'rb'))
    secrets = load(open(conf['SECRETS'], 'rb'))
    if not test:
        conf['USERNAME'] = secrets['hactar']['username']
        conf['PASSWORD'] = secrets['hactar']['password']
        app.config.update(conf)
    

    logpath = os.path.join(conf['LOG_DIR'], conf['LOG_MAIN'])
    handler = RotatingFileHandler(logpath, maxBytes=100000,
            backupCount=4)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

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
