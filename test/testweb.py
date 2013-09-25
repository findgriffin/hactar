# -*- coding: utf-8 -*-
"""
    web Tests
    ~~~~~~~~~~~~

    Tests the web application based on web_tests.py by Armin Ronacher.

    :license: BSD, see LICENSE for more details.
"""
import unittest
from hashlib import sha1
import datetime

from flask.ext.testing import TestCase

from web import db
import web

class TestWeb(TestCase):

    uri0 = 'http://foobar.com'
    desc0 = 'a description of foobar'
    uri1 = 'http://foobar.com/stuff'
    desc1 = 'a description of stuff'
    uri2 = 'http://foobar.com/stuff/more'
    desc2 = 'a description of foobar/stuff/more'

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


    def check_nugget(self, resp, uri, desc, new=True, flash=None):
        if flash:
            msg = flash
        elif new:
            msg = 'New nugget was successfully added'
        else:
            msg = 'Nugget successfully modified'
        now = datetime.datetime.now()
        then = now - datetime.timedelta(minutes=1)
        now = now.strftime('%H:%M %d/%m/%Y')
        then = then.strftime('%H:%M %d/%m/%Y')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<li><h2><a href="%s">%s</a></h2>' % (uri, uri), resp.data)
        self.assertIn('<br>%s' % desc, resp.data)
        try:
            self.assertIn('modified:%s' % now, resp.data)
        except AssertionError:
            self.assertIn('modified:%s' % now, resp.data)
        if new:
            self.assertIn(msg, resp.data)
            try:
                self.assertIn('added:%s' % now, resp.data)
            except AssertionError:
                self.assertIn('added:%s' % then, resp.data)
        else:
            self.assertIn(msg, resp.data)
            try:
                self.assertNotIn('added:%s' % now, resp.data)
            except AssertionError:
                self.assertNotIn('added:%s' % then, resp.data)
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
        rv = self.client.post('/add', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_nugget(rv, self.uri0, self.desc0)

    def test_add_nuggets(self):
        """Test adding some nuggets with flask"""
        self.login()
        rv0 = self.client.post('/add', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_nugget(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/add', data=dict( uri=self.uri1, desc=self.desc1,
        ), follow_redirects=True)
        self.check_nugget(rv1, self.uri0, self.desc0)
        self.check_nugget(rv1, self.uri1, self.desc1)
        rv2 = self.client.post('/add', data=dict( uri=self.uri2, desc=self.desc2,
        ), follow_redirects=True)
        self.check_nugget(rv2, self.uri0, self.desc0)
        self.check_nugget(rv2, self.uri1, self.desc1)
        self.check_nugget(rv2, self.uri2, self.desc2)

    def test_dup_nuggets(self):
        """Test attempting to add duplicate nuggets"""
        self.login()
        rv0 = self.client.post('/add', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_nugget(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/add', data=dict( uri=self.uri0, desc=self.desc1,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        errstr = 'Nugget with that URI or description already exists'
        self.check_nugget(rv1, self.uri0, self.desc0, flash=errstr)
        self.assertNotIn('<br>%s' % self.desc1, rv1.data)

    def test_update_nugget(self):
        self.login()
        rv0 = self.client.post('/add', data=dict( uri=self.uri0, desc=self.desc0),
            follow_redirects=True)
        self.check_nugget(rv0, self.uri0, self.desc0, new=True)
        nugget_id = int(sha1(self.uri0).hexdigest()[:15], 16)
        self.assertIn('<a href="/edit/%s">edit</a>' % nugget_id, rv0.data)
        rv1 = self.client.post('/update/%s' % nugget_id, data=dict(text=self.desc1),
                follow_redirects=True)
        self.check_nugget(rv1, self.uri0, self.desc1, new=False)
        self.assertNotIn('<br>%s' % self.desc0, rv1.data)
    
    def test_delete_nugget(self):
        self.login()
        rv0 = self.client.post('/add', data=dict( uri=self.uri0, desc=self.desc0),
            follow_redirects=True)
        self.check_nugget(rv0, self.uri0, self.desc0, new=True)
        rv1 = self.client.post('/add', data=dict( uri=self.uri1, desc=self.desc1),
            follow_redirects=True)
        self.check_nugget(rv1, self.uri1, self.desc1, new=True)

        # delete nugget 0
        nugget_id = int(sha1(self.uri0).hexdigest()[:15], 16)
        self.assertIn('<a href="/edit/%s">edit</a>' % nugget_id, rv0.data)
        rv2 = self.client.get('/edit/%s' % nugget_id,
                follow_redirects=True)
        self.assertIn('<form action="/delete/%s" method=post' % nugget_id, rv2.data)
        self.assertIn('<input type=submit value=Delete', rv2.data)
        rv3 = self.client.post('/delete/%s' % nugget_id, follow_redirects=True)
        self.check_nugget(rv3, self.uri1, self.desc1, new=False, 
                    flash='Nugget successfully deleted')
        self.assertNotIn('<br>%s' % self.desc0, rv3.data)


if __name__ == '__main__':
    unittest.main()
