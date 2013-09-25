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
    uri1 = 'http://stuff.com/somewhere'
    desc1 = 'a description of stuff'
    uri2 = 'http://more.com/somewhere'
    desc2 = 'a description of more'

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
            self.assertIn(flash, resp.data)
        elif new:
            msg = 'New nugget was successfully added'
            self.assertIn(msg, resp.data)
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
            try:
                self.assertIn('added:%s' % now, resp.data)
            except AssertionError:
                self.assertIn('added:%s' % then, resp.data)
        else:
            try:
                self.assertNotIn('added:%s' % now, resp.data)
            except AssertionError:
                self.assertNotIn('added:%s' % then, resp.data)
    # testing functions

    def test_empty_db(self):
        """Start with a blank database."""
        rv = self.client.get('/nuggets')
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
        rv = self.client.post('/nuggets', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_nugget(rv, self.uri0, self.desc0)

    def test_add_nuggets(self):
        """Test adding some nuggets with flask"""
        self.login()
        rv0 = self.client.post('/nuggets', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_nugget(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/nuggets', data=dict( uri=self.uri1, desc=self.desc1,
        ), follow_redirects=True)
        self.check_nugget(rv1, self.uri0, self.desc0)
        self.check_nugget(rv1, self.uri1, self.desc1)
        rv2 = self.client.post('/nuggets', data=dict( uri=self.uri2, desc=self.desc2,
        ), follow_redirects=True)
        self.check_nugget(rv2, self.uri0, self.desc0)
        self.check_nugget(rv2, self.uri1, self.desc1)
        self.check_nugget(rv2, self.uri2, self.desc2)

    def test_dup_nuggets(self):
        """Test attempting to add duplicate nuggets"""
        self.login()
        rv0 = self.client.post('/nuggets', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_nugget(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/nuggets', data=dict( uri=self.uri0, desc=self.desc1,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        errstr = 'Nugget with that URI or description already exists'
        self.check_nugget(rv1, self.uri0, self.desc0, flash=errstr)
        self.assertNotIn('<br>%s' % self.desc1, rv1.data)

    def test_update_nugget(self):
        self.login()
        rv0 = self.client.post('/nuggets', data=dict( uri=self.uri0, desc=self.desc0),
            follow_redirects=True)
        self.check_nugget(rv0, self.uri0, self.desc0, new=True)
        nugget_id = int(sha1(self.uri0).hexdigest()[:15], 16)
        self.assertIn('<a href="/nuggets/%s">edit</a>' % nugget_id, rv0.data)
        rv1 = self.client.post('/nuggets/%s' % nugget_id, data=dict(text=self.desc1),
                follow_redirects=True)
        self.check_nugget(rv1, self.uri0, self.desc1, new=False,
            flash='Nugget successfully modified')
        self.assertNotIn('<br>%s' % self.desc0, rv1.data)
    
    def test_delete_nugget(self):
        self.login()
        rv0 = self.client.post('/nuggets', data=dict( uri=self.uri0, desc=self.desc0),
            follow_redirects=True)
        self.check_nugget(rv0, self.uri0, self.desc0, new=True)
        rv1 = self.client.post('/nuggets', data=dict( uri=self.uri1, desc=self.desc1),
            follow_redirects=True)
        self.check_nugget(rv1, self.uri1, self.desc1, new=True)

        # delete nugget 0
        nugget_id = int(sha1(self.uri0).hexdigest()[:15], 16)
        self.assertIn('<a href="/nuggets/%s">edit</a>' % nugget_id, rv0.data)
        rv2 = self.client.get('/nuggets/%s' % nugget_id,
                follow_redirects=True)
        formstr = '<form action="/nuggets/%s" method="post"' 
        self.assertIn(formstr % nugget_id, rv2.data)
        dl='<input type="checkbox" name="delete" value="Delete">delete</input>'
        self.assertIn(dl, rv2.data)
        rv3 = self.client.post('/nuggets/%s' % nugget_id, data=dict(
            delete='Delete'), follow_redirects=True)
        self.check_nugget(rv3, self.uri1, self.desc1, new=False, 
                    flash='Nugget successfully deleted')
        self.assertNotIn('<br>%s' % self.desc0, rv3.data)

    def test_search_nuggets(self):
        self.login()
        # add 3 nuggets to get us started
        rv0 = self.client.post('/nuggets', data=dict( uri=self.uri0, desc=self.desc0),
            follow_redirects=True)
        rv1 = self.client.post('/nuggets', data=dict( uri=self.uri1, desc=self.desc1),
            follow_redirects=True)
        rv2 = self.client.post('/nuggets', data=dict( uri=self.uri2, desc=self.desc2),
            follow_redirects=True)
        rv3 = self.client.get('/nuggets?q=description', follow_redirects=True)
        self.check_nugget(rv3, self.uri0, self.desc0, new=False)
        self.check_nugget(rv3, self.uri1, self.desc1, new=False)
        self.check_nugget(rv3, self.uri2, self.desc2, new=False)
        rv4 = self.client.get('/nuggets?q=stuff', follow_redirects=True)
        self.check_nugget(rv4, self.uri1, self.desc1, new=False)
        self.assertNotIn(self.desc0, rv4.data)
        self.assertNotIn(self.desc2, rv4.data)
        rv5 = self.client.get('/nuggets?q=more', follow_redirects=True)
        self.check_nugget(rv5, self.uri2, self.desc2, new=False)
        self.assertNotIn(self.desc0, rv5.data)
        self.assertNotIn(self.desc1, rv5.data)
        rv6 = self.client.get('/nuggets?q=somewhere', follow_redirects=True)
        self.check_nugget(rv6, self.uri1, self.desc1, new=False)
        self.check_nugget(rv6, self.uri2, self.desc2, new=False)
        self.assertNotIn(self.desc0, rv5.data)


if __name__ == '__main__':
    unittest.main()
