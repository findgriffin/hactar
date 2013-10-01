import unittest
from hashlib import sha1
import shutil
import re

from flask.ext.testing import TestCase
from nose.tools import set_trace;

from app import db, app
import hactar.models
from hactar import scraper

class TestScraper(TestCase):

    _multiprocess_can_split = False

    def create_app(self):
        import json
        self.conf = json.load(open('config.json', 'rb'))['test2']
        app.config.update(self.conf)
        hactar.models.setup('test')
        app.logger.setLevel(30)
        app.celery_running = False
        return app

    def setUp(self):
        """Before each test, set up a blank database"""
        try:
            shutil.rmtree(self.conf['WHOOSH_BASE'])
        except OSError as err:
            pass
        hactar.models.setup('test')
        db.create_all()

    def tearDown(self):
        """Get rid of the database again after each test."""
        db.session.remove()
        db.drop_all()

    def login(self, username=None, password=None):
        if not username:
            username = app.config['USERNAME']
        if not password:
            password = app.config['PASSWORD']
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def check_meme(self, resp, uri, desc, new=True, flash=None, isuri=True,
            logged_in=True):
        if flash:
            self.assertIn(flash, resp.data)
        elif new:
            msg = 'New meme was successfully added'
            self.assertIn(msg, resp.data)
        now = 'just now'
        self.assertEqual(resp.status_code, 200)
        meme_id = int(sha1(uri).hexdigest()[:15], 16)
        if logged_in:
            self.assertIn('<ahref="/memes/%s">(edit)</a>' % meme_id,
                    re.sub('\s+', '', resp.data))
        else:
            self.assertIn('<ahref="/memes/%s">(view)</a>' % meme_id,
                    re.sub('\s+', '', resp.data))
        if isuri:
            self.assertIn('<h4><a href="%s" target="_blank">%s</a>' % (uri, uri), resp.data)
        else:
            self.assertIn('<h4>%s' % uri, resp.data)
        self.assertIn('<p>%s</p>' % desc, resp.data)
        self.assertIn('%s</small></h4>' % now, resp.data)
        return meme_id

    def test_simple(self):
        """Start with a blank database."""
        self.login()
        uri = 'http://localhost:5000/memes'
        meme_id = int(sha1(uri).hexdigest()[:15], 16)
        rv = self.client.post('/memes', data=dict( uri=uri, desc='a b'), 
                follow_redirects=True)
        cookie_jar = self.client.cookie_jar._cookies
        cookie = cookie_jar['localhost.local']['/']['session'].value
        status = scraper.crawl(meme_id, uri, {'session': cookie})
        self.assertEqual(status, 200)

