"""Tests for the hactar api"""
from hashlib import sha1
import shutil
import re
import json

from app import db, app
from base import BaseTest
from hactar.models import is_uri

class TestApi(BaseTest):

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

