# -*- coding: utf-8 -*-
"""
    web Tests
    ~~~~~~~~~~~~

"""
from hashlib import sha1
import shutil
import re
import json

from app import db, app
from base import BaseTest

class TestWeb(BaseTest):

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
        rv = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0,
        ), follow_redirects=True)
        self.check_meme(rv, self.uri0, self.desc0)

    def test_add_memes(self):
        """Test adding some memes with flask"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0,
        ), follow_redirects=True)
        self.check_meme(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/memes', data=dict( what=self.uri1, why=self.desc1,
        ), follow_redirects=True)
        self.check_meme(rv1, self.uri0, self.desc0)
        self.check_meme(rv1, self.uri1, self.desc1)
        rv2 = self.client.post('/memes', data=dict( what=self.uri2, why=self.desc2,
        ), follow_redirects=True)
        self.check_meme(rv2, self.uri0, self.desc0)
        self.check_meme(rv2, self.uri1, self.desc1)
        self.check_meme(rv2, self.uri2, self.desc2)

    def test_dup_memes(self):
        """Test attempting to add duplicate memes"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0,
        ), follow_redirects=True)
        self.check_meme(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc1,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        errstr = 'Meme with that URI or description already exists'
        self.check_meme(rv1, self.uri0, self.desc0, flash=errstr)
        self.assertNotIn('<br>%s' % self.desc1, rv1.data)

    def test_update_meme(self):
        """Test updating a meme"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme(rv0, self.uri0, self.desc0, new=True)
        rv1 = self.client.post('/memes/%s' % meme_id, data=dict(why=self.desc1),
                follow_redirects=True)
        self.check_meme(rv1, self.uri0, self.desc1, new=False,
            flash='Meme successfully modified')
        self.assertNotIn(self.desc0, rv1.data)
    
    def test_delete_meme(self):
        """Test deleting a meme"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme(rv0, self.uri0, self.desc0, new=True)
        rv1 = self.client.post('/memes', data=dict( what=self.uri1, why=self.desc1),
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
                    flash='Meme deleted')
        self.assertNotIn('<br>%s' % self.desc0, rv3.data)

        # try to delete it again
        rv4 = self.client.post('/memes/%s' % meme_id, data=dict(
            delete='Delete'), follow_redirects=True)
        self.check_meme(rv4, self.uri1, self.desc1, new=False, 
                    flash='Meme deleted')


    def test_search_memes(self):
        """Test basic meme searching"""
        self.login()
        # add 3 memes to get us started
        rv0 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        rv1 = self.client.post('/memes', data=dict( what=self.uri1, why=self.desc1),
            follow_redirects=True)
        rv2 = self.client.post('/memes', data=dict( what=self.uri2, why=self.desc2),
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

    def test_update_search(self):
        """Test updating and then searching for a meme"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme(rv0, self.uri0, self.desc0, new=True)
        rv1 = self.client.post('/memes/%s' % meme_id, data=dict(why=self.desc1),
                follow_redirects=True)
        self.check_meme(rv1, self.uri0, self.desc1, new=False,
            flash='Meme successfully modified')
        rv2 = self.client.get('/memes?q=stuff', follow_redirects=True)
        self.assertNotIn(self.desc0, rv2.data)
        self.assertIn(self.desc1, rv2.data)

    def test_title_memes(self):
        """Test adding memes with title (no URL)"""
        self.login()
        rv = self.client.post('/memes', data=dict( what=self.title0, why=self.desc4,
        ), follow_redirects=True)
        self.check_meme(rv, self.title0, self.desc4, isuri=False)

    def test_logged_out_views(self):
        """Test page appearance when logged out"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0,
        ), follow_redirects=True)
        rv1 = self.client.post('/memes', data=dict( what=self.uri1, why=self.desc1,
        ), follow_redirects=True)
        rv2 = self.client.post('/memes', data=dict( what=self.uri2, why=self.desc2,
        ), follow_redirects=True)
        self.assertIn('<textarea', rv2.data)
        self.assertIn('method="post"', rv2.data)
        self.logout()
        rv3 = self.client.get('/memes', follow_redirects=True)
        self.assertNotIn('<textarea', rv3.data)
        self.assertNotIn('method="post"', rv3.data)
        meme0 = self.check_meme(rv3, self.uri0, self.desc0,
                logged_in=False, new=False)
        meme1 = self.check_meme(rv3, self.uri1, self.desc1,
                logged_in=False, new=False)
        meme2 = self.check_meme(rv3, self.uri2, self.desc2,
                logged_in=False, new=False)
        rv4 = self.client.get('/memes/%s' % meme0, follow_redirects=True)
        self.assertNotIn('<textarea', rv4.data)
        self.assertNotIn('method="post"', rv4.data)


    def test_update_fail(self):
        """Test updating a nonexistant meme"""
        self.login()
        rv0 = self.client.post('/memes', data=dict(what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme(rv0, self.uri0, self.desc0, new=True) - 10
        rv1 = self.client.post('/memes/%s' % meme_id, data=dict(why=self.desc1),
                follow_redirects=True)
        self.assertEquals(404, rv1.status_code)

    def test_code_snippet(self):
        self.login()
        code_md = """
This is a description:

    #! /usr/bin/env python
    def hello_world():
        print "Hello, world!"
"""
        code_html = """<p>This is a description:</p>
<pre><code>#! /usr/bin/env python
def hello_world():
    print "Hello, world!"
</code></pre>
"""
        rv = self.client.post('/memes', data=dict( what=self.uri0, why=code_md,
        ), follow_redirects=True)
        self.check_meme(rv, self.uri0, 'This is a description:')
        self.assertIn(code_html, rv.data)

    def test_modified_times(self):
        """Check that modified and checked times get updated"""
        self.skipTest('not implemented yet')

    def test_update_content(self):
        """Check that we can update the content of a meme"""
        self.login()
        rv0 = self.client.post('/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme(rv0, self.uri0, self.desc0, new=True)
        content = 'page content'
        title = 'super duper title'
        rv1 = self.client.post('/memes/%s' % meme_id,
                data=dict(content=content, title=title, status_code=200),
                follow_redirects=True)
        result = json.loads(rv1.data)
        self.assertEquals(result[unicode(meme_id)], True)
        rv2 = self.client.get('/memes?q=duper', follow_redirects=True)
        self.assertIn(self.desc0, rv2.data)
        self.assertIn(title, rv2.data)
        
