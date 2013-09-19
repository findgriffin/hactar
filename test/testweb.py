# -*- coding: utf-8 -*-
"""
    web Tests
    ~~~~~~~~~~~~

    Tests the web application based on web_tests.py by Armin Ronacher.

    :license: BSD, see LICENSE for more details.
"""
import os
import web
import unittest
import tempfile


class TestWeb(unittest.TestCase):

    def setUp(self):
        """Before each test, set up a blank database"""
        self.db_fd, web.app.config['DATABASE'] = tempfile.mkstemp()
        web.app.config['TESTING'] = True
        self.app = web.app.test_client()
        web.init_db()

    def tearDown(self):
        """Get rid of the database again after each test."""
        os.close(self.db_fd)
        os.unlink(web.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # testing functions

    def test_empty_db(self):
        """Start with a blank database."""
        rv = self.app.get('/')
        self.assertIn('No nuggets here so far', rv.data)

    def test_login_logout(self):
        """Make sure login and logout works"""
        rv = self.login(web.app.config['USERNAME'],
                        web.app.config['PASSWORD'])
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
        self.login(web.app.config['USERNAME'],
                   web.app.config['PASSWORD'])
        uri = 'http://foobar.com'
        desc = 'a description of foobar'
        rv = self.app.post('/add', data=dict( uri=uri, desc=desc,
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn('<li><h2>%s</h2>%s' % (uri, desc), rv.data)

    def test_add_nuggets(self):
        """Test adding some nuggets with flask"""
        self.login(web.app.config['USERNAME'],
                   web.app.config['PASSWORD'])
        uri0 = 'http://foobar.com'
        desc0 = 'a description of foobar'
        uri1 = 'http://foobar.com/stuff'
        desc1 = 'a description of foobar/stuff'
        uri2 = 'http://foobar.com/stuff/more'
        desc2 = 'a description of foobar/stuff/more'
        rv0 = self.app.post('/add', data=dict( uri=uri0, desc=desc0,
        ), follow_redirects=True)
        rv1 = self.app.post('/add', data=dict( uri=uri1, desc=desc1,
        ), follow_redirects=True)
        rv2 = self.app.post('/add', data=dict( uri=uri2, desc=desc2,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        self.assertIn('<li><h2>%s</h2>%s' % (uri0, desc0), rv2.data)
        self.assertIn('<li><h2>%s</h2>%s' % (uri1, desc1), rv2.data)
        self.assertIn('<li><h2>%s</h2>%s' % (uri2, desc2), rv2.data)

    def test_dup_nuggets(self):
        """Test attempting to add duplicate nuggets"""
        self.login(web.app.config['USERNAME'],
                   web.app.config['PASSWORD'])
        uri0 = 'http://foobar.com'
        desc0 = 'a description of foobar'
        uri1 = uri0
        desc1 = 'a description of foobar/stuff'
        rv0 = self.app.post('/add', data=dict( uri=uri0, desc=desc0,
        ), follow_redirects=True)
        rv1 = self.app.post('/add', data=dict( uri=uri1, desc=desc1,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        errstr = 'Nugget with that URI or description already exists'
        self.assertIn('<div class=flash>%s</div>' % errstr, rv1.data)
        self.assertIn('<li><h2>%s</h2>%s' % (uri0, desc0), rv1.data)
        self.assertNotIn('<li><h2>%s</h2>%s' % (uri1, desc1), rv1.data)

if __name__ == '__main__':
    unittest.main()
