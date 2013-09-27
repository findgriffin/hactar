#! /usr/bin/env python
import logging
from logging.handlers import RotatingFileHandler
from json import load

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import app


def main():
    """Start tornado running hactar."""
    config = load(open('config.json', 'rb'))
    app.config.update(config)

    handler = RotatingFileHandler(config['LOG_LOCATION'], maxBytes=100000,
            backupCount=4)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8080)
    IOLoop.instance().start()


if __name__ == "__main__":
    main()
