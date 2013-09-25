# -*- coding: utf-8 -*-
"""
    web Tests
    ~~~~~~~~~~~~

    Tests the web application based on web_tests.py by Armin Ronacher.

    :license: BSD, see LICENSE for more details.
"""
import unittest
from hashlib import sha1

from flask.ext.testing import TestCase

from web import db
import web

class TestWeb(TestCase):

    def create_app(self):
        app = web.app
        app.config.update(dict(
            SQLALCHEMY_DATABASE_URI='sqlite:///')
            )
        return app

    def setUp(self):
        """Before each test, set up a blank database"""
        db.create_all()

    def tearDown(self):
        """Get rid of the database again after each test."""
        db.session.remove()
        db.drop_all()

    def login(self, username=None, password=None):
        if not username:
            username = web.app.config['USERNAME']
        if not password:
            password = web.app.config['PASSWORD']
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    # testing functions

    def test_empty_db(self):
        """Start with a blank database."""
        rv = self.client.get('/')
        self.assertIn('No nuggets here so far', rv.data)

    def test_login_logout(self):
        """Make sure login and logout works"""
        rv = self.login()
        self.assertIn(b'You were logged in', rv.data)
        rv = self.logout()
        self.assertIn(b'You were logged out', rv.data)
        rv = self.login(web.app.config['USERNAME'] + 'x',
                        web.app.config['PASSWORD'])
        self.assertIn(b'Invalid username', rv.data)
        rv = self.login(web.app.config['USERNAME'],
                        web.app.config['PASSWORD'] + 'x')
        self.assertIn(b'Invalid password', rv.data)

    def test_add_nugget(self):
        """Test adding a nugget with flask"""
        self.login()
        uri = 'http://foobar.com'
        desc = 'a description of foobar'
        rv = self.client.post('/add', data=dict( uri=uri, desc=desc,
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn('<li><h2><a href="%s">%s</a></h2>' % (uri, uri), rv.data)
        self.assertIn('<br>%s' % desc, rv.data)

    def test_add_nuggets(self):
        """Test adding some nuggets with flask"""
        self.login()
        uri0 = 'http://foobar.com'
        desc0 = 'a description of foobar'
        uri1 = 'http://foobar.com/stuff'
        desc1 = 'a description of foobar/stuff'
        uri2 = 'http://foobar.com/stuff/more'
        desc2 = 'a description of foobar/stuff/more'
        rv0 = self.client.post('/add', data=dict( uri=uri0, desc=desc0,
        ), follow_redirects=True)
        rv1 = self.client.post('/add', data=dict( uri=uri1, desc=desc1,
        ), follow_redirects=True)
        rv2 = self.client.post('/add', data=dict( uri=uri2, desc=desc2,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        self.assertIn('New nugget was successfully added', rv0.data)
        self.assertIn('New nugget was successfully added', rv1.data)
        self.assertIn('New nugget was successfully added', rv2.data)
        self.assertIn('<li><h2><a href="%s">%s</a></h2>' % (uri0, uri0), rv2.data)
        self.assertIn('<br>%s' % desc0, rv2.data)
        self.assertIn('<li><h2><a href="%s">%s</a></h2>' % (uri1, uri1), rv2.data)
        self.assertIn('<br>%s' % desc1, rv2.data)
        self.assertIn('<li><h2><a href="%s">%s</a></h2>' % (uri2, uri2), rv2.data)
        self.assertIn('<br>%s' % desc2, rv2.data)

    def test_dup_nuggets(self):
        """Test attempting to add duplicate nuggets"""
        self.login()
        uri0 = 'http://foobar.com'
        desc0 = 'a description of foobar'
        uri1 = uri0
        desc1 = 'a description of foobar/stuff'
        rv0 = self.client.post('/add', data=dict( uri=uri0, desc=desc0,
        ), follow_redirects=True)
        rv1 = self.client.post('/add', data=dict( uri=uri1, desc=desc1,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        errstr = 'Nugget with that URI or description already exists'
        self.assertIn('<div class=flash>%s</div>' % errstr, rv1.data)
        self.assertIn('<li><h2><a href="%s">%s</a></h2>' % (uri0, uri0), rv1.data)
        self.assertIn('<br>%s' % desc0, rv1.data)
        self.assertNotIn('<br>%s' % desc1, rv1.data)

    def test_update_nugget(self):
        self.login()
        uri0 = 'http://foobar.com'
        desc0 = 'a description of foobar'
        desc1 = 'a description of stuff'
        rv0 = self.client.post('/add', data=dict( uri=uri0, desc=desc0),
            follow_redirects=True)
        self.assertEqual(rv0.status_code, 200)
        self.assertIn('<li><h2><a href="%s">%s</a></h2>' % (uri0, uri0), rv0.data)
        self.assertIn('<br>%s' % desc0, rv0.data)
        self.assertNotIn('<br>%s' % desc1, rv0.data)
        nugget_id = int(sha1(uri0).hexdigest()[:15], 16)
        self.assertIn('<a href="/edit/%s">edit</a>' % nugget_id, rv0.data)
        rv1 = self.client.post('/update/%s' % nugget_id, data=dict(text=desc1),
                follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        self.assertIn('<br>%s' % desc1, rv1.data)
        self.assertNotIn('<br>%s' % desc0, rv1.data)

if __name__ == '__main__':
    unittest.main()
