"""Tests for the hactar api"""
from hashlib import sha1
import shutil
import re
import json

from app import db, app
from base import BaseApi

class TestApi(BaseApi):

    # testing functions
    def test_empty_db(self):
        """Start with a blank database (via api)."""
        rv = self.client.get('/api/memes', follow_redirects=True)
        self.assertEquals(rv.status_code, 200)
        self.assertEquals({'memes': [], 'flashes': []}, json.loads(rv.data))

    def test_add_meme(self):
        """Test adding a meme (via api)"""
        self.login()
        rv = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0,
        ), follow_redirects=True)
        self.check_meme_json(rv, self.uri0, self.desc0)

    def test_login_logout(self):
        self.skipTest('Only support html login for now')

    def test_add_memes(self):
        """Tes adding memes (with api)"""
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0,
        ), follow_redirects=True)
        self.check_meme_json(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/api/memes', data=dict( what=self.uri1, why=self.desc1,
        ), follow_redirects=True)
        self.check_meme_json(rv1, self.uri0, self.desc0, new=True, last=False)
        self.check_meme_json(rv1, self.uri1, self.desc1)
        rv2 = self.client.post('/api/memes', data=dict( what=self.uri2, why=self.desc2,
        ), follow_redirects=True)
        self.check_meme_json(rv2, self.uri0, self.desc0, new=True, last=False)
        self.check_meme_json(rv2, self.uri1, self.desc1, new=True, last=False)
        self.check_meme_json(rv2, self.uri2, self.desc2)
    def test_dup_memes(self):
        """Test adding duplicate memes (with api)"""
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0,
        ), follow_redirects=True)
        self.check_meme_json(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc1,
        ), follow_redirects=True)
        self.assertEqual(rv1.status_code, 200)
        errstr = 'Meme with that URI or description already exists'
        self.check_meme_json(rv1, self.uri0, self.desc0, flash=errstr)
        self.assertNotIn('<br>%s' % self.desc1, rv1.data)
    def test_update_meme(self):
        self.skipTest('Not implemented yet')
    def test_delete_meme(self):
        self.skipTest('Not implemented yet')
    def test_search_memes(self):
        self.skipTest('Not implemented yet')
    def test_update_search(self):
        self.skipTest('Not implemented yet')
    def test_title_memes(self):
        self.skipTest('Not implemented yet')
    def test_logged_out_views(self):
        self.skipTest('Not implemented yet')
    def test_update_fail(self):
        self.skipTest('Not implemented yet')
    def test_code_snippet(self):
        self.skipTest('Not implemented yet')
    def test_modified_times(self):
        self.skipTest('Not implemented yet')
    def test_update_content(self):
        self.skipTest('Not implemented yet')
