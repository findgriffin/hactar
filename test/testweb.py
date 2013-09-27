# -*- coding: utf-8 -*-
"""
    web Tests
    ~~~~~~~~~~~~

"""
import unittest
from hashlib import sha1

from flask.ext.testing import TestCase

from app import db, app, config_app

class TestWeb(TestCase):

    uri0 = 'http://foobar.com'
    desc0 = 'a description of foobar'
    uri1 = 'http://stuff.com/somewhere'
    desc1 = 'a description of stuff'
    uri2 = 'http://more.com/somewhere'
    desc2 = 'a description of more'
    title0 = 'A title not a URI'
    desc4 = 'a description of this "not-URI"'

    def create_app(self):
        config_app(app)
        app.config.update(dict(
            SQLALCHEMY_DATABASE_URI='sqlite:///')
            )
        app.logger.setLevel(30)
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
            username = app.config['USERNAME']
        if not password:
            password = app.config['PASSWORD']
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)


    def check_meme(self, resp, uri, desc, new=True, flash=None, isuri=True):
        if flash:
            self.assertIn(flash, resp.data)
        elif new:
            msg = 'New meme was successfully added'
            self.assertIn(msg, resp.data)
        now = 'just now'
        self.assertEqual(resp.status_code, 200)
        meme_id = int(sha1(uri).hexdigest()[:15], 16)
        self.assertIn('<a href="/memes/%s">(edit)</a>' % meme_id, resp.data)
        if isuri:
            self.assertIn('<h4><a href="%s" target="_blank">%s</a>' % (uri, uri), resp.data)
        else:
            self.assertIn('<h4>%s' % uri, resp.data)
        self.assertIn('<p>%s</p>' % desc, resp.data)
        self.assertIn('%s</small></h4>' % now, resp.data)
        return meme_id
    # testing functions

    def test_empty_db(self):
        """Start with a blank database."""
        rv = self.client.get('/memes')
        self.assertIn('No memes here so far', rv.data)

    def test_login_logout(self):
        """Make sure login and logout works"""
        rv = self.login()
        self.assertIn(b'You were logged in', rv.data)
        rv = self.logout()
        self.assertIn(b'You were logged out', rv.data)
        rv = self.login(app.config['USERNAME'] + 'x',
                        app.config['PASSWORD'])
        self.assertIn(b'Invalid username', rv.data)
        rv = self.login(app.config['USERNAME'],
                        app.config['PASSWORD'] + 'x')
        self.assertIn(b'Invalid password', rv.data)

    def test_add_meme(self):
        """Test adding a meme with flask"""
        self.login()
        rv = self.client.post('/memes', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_meme(rv, self.uri0, self.desc0)

    def test_add_memes(self):
        """Test adding some memes with flask"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_meme(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/memes', data=dict( uri=self.uri1, desc=self.desc1,
        ), follow_redirects=True)
        self.check_meme(rv1, self.uri0, self.desc0)
        self.check_meme(rv1, self.uri1, self.desc1)
        rv2 = self.client.post('/memes', data=dict( uri=self.uri2, desc=self.desc2,
        ), follow_redirects=True)
        self.check_meme(rv2, self.uri0, self.desc0)
        self.check_meme(rv2, self.uri1, self.desc1)
        self.check_meme(rv2, self.uri2, self.desc2)

    def test_dup_memes(self):
        """Test attempting to add duplicate memes"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( uri=self.uri0, desc=self.desc0,
        ), follow_redirects=True)
        self.check_meme(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/memes', data=dict( uri=self.uri0, desc=self.desc1,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        errstr = 'Meme with that URI or description already exists'
        self.check_meme(rv1, self.uri0, self.desc0, flash=errstr)
        self.assertNotIn('<br>%s' % self.desc1, rv1.data)

    def test_update_meme(self):
        """Test updating a meme"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( uri=self.uri0, desc=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme(rv0, self.uri0, self.desc0, new=True)
        rv1 = self.client.post('/memes/%s' % meme_id, data=dict(text=self.desc1),
                follow_redirects=True)
        self.check_meme(rv1, self.uri0, self.desc1, new=False,
            flash='Meme successfully modified')
        self.assertNotIn('<br>%s' % self.desc0, rv1.data)
    
    def test_delete_meme(self):
        """Test deleting a meme"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( uri=self.uri0, desc=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme(rv0, self.uri0, self.desc0, new=True)
        rv1 = self.client.post('/memes', data=dict( uri=self.uri1, desc=self.desc1),
            follow_redirects=True)
        self.check_meme(rv1, self.uri1, self.desc1, new=True)

        # delete meme 0
        rv2 = self.client.get('/memes/%s' % meme_id,
                follow_redirects=True)
        formstr = '<form action="/memes/%s" method="post"' 
        self.assertIn(formstr % meme_id, rv2.data)
        dl='<input type="checkbox" name="delete" value="Delete">delete</input>'
        self.assertIn(dl, rv2.data)
        rv3 = self.client.post('/memes/%s' % meme_id, data=dict(
            delete='Delete'), follow_redirects=True)
        self.check_meme(rv3, self.uri1, self.desc1, new=False, 
                    flash='Meme successfully deleted')
        self.assertNotIn('<br>%s' % self.desc0, rv3.data)

    def test_search_memes(self):
        """Test basic meme searching"""
        self.login()
        # add 3 memes to get us started
        rv0 = self.client.post('/memes', data=dict( uri=self.uri0, desc=self.desc0),
            follow_redirects=True)
        rv1 = self.client.post('/memes', data=dict( uri=self.uri1, desc=self.desc1),
            follow_redirects=True)
        rv2 = self.client.post('/memes', data=dict( uri=self.uri2, desc=self.desc2),
            follow_redirects=True)
        rv3 = self.client.get('/memes?q=description', follow_redirects=True)
        self.check_meme(rv3, self.uri0, self.desc0, new=False)
        self.check_meme(rv3, self.uri1, self.desc1, new=False)
        self.check_meme(rv3, self.uri2, self.desc2, new=False)
        rv4 = self.client.get('/memes?q=stuff', follow_redirects=True)
        self.check_meme(rv4, self.uri1, self.desc1, new=False)
        self.assertNotIn(self.desc0, rv4.data)
        self.assertNotIn(self.desc2, rv4.data)
        rv5 = self.client.get('/memes?q=more', follow_redirects=True)
        self.check_meme(rv5, self.uri2, self.desc2, new=False)
        self.assertNotIn(self.desc0, rv5.data)
        self.assertNotIn(self.desc1, rv5.data)
        rv6 = self.client.get('/memes?q=somewhere', follow_redirects=True)
        self.check_meme(rv6, self.uri1, self.desc1, new=False)
        self.check_meme(rv6, self.uri2, self.desc2, new=False)
        self.assertNotIn(self.desc0, rv5.data)

    def test_title_memes(self):
        """Test adding memes with title (no URL)"""
        self.login()
        rv = self.client.post('/memes', data=dict( uri=self.title0, desc=self.desc4,
        ), follow_redirects=True)
        self.check_meme(rv, self.title0, self.desc4, isuri=False)

    def test_logged_out_views(self):
        """Test page appearance when logged out"""
        self.skipTest(True)

    def test_delete_fail(self):
        """Test attempting to delete a nonexistant meme"""
        self.skipTest(True)

    def test_update_fail(self):
        """Test updating a nonexistant meme"""
        self.skipTest(True)

    def test_add_no_uri(self):
        """Test adding a meme with no uri"""
        self.skipTest(True)
    def test_code_snippet(self):
        self.skipTest(True)

if __name__ == '__main__':
    unittest.main()
