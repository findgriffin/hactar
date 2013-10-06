"""Tests for the hactar api"""
import json
from dateutil.parser import parse

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
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme_json(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/api/memes/%s' % meme_id, data=dict(why=self.desc1),
                follow_redirects=True)
        
        rjson = json.loads(rv1.data)
        self.assertEquals(rv1.status_code, 200)
        self.assertEquals(rjson['uri'], self.uri0)
        self.assertEquals(rjson['text'], self.desc1)
        self.assertEquals(rjson['status_code'], u'-1')
        self.assertEquals(rjson['id'], unicode(meme_id))
        modified = parse(rjson['modified'])
        added = parse(rjson['added'])
        self.assertTrue(modified > added)

    def test_delete_meme(self):
        """Test deleting a meme (with api)"""
        self.login()
        rv0 = self.client.post('/api/memes', data=dict(what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme_json(rv0, self.uri0, self.desc0, new=True)
        rv1 = self.client.delete('/api/memes/%s' % meme_id)
        self.assertEquals(rv1.status_code, 200)
        self.assertEquals(json.loads(rv1.data), 
                {unicode(meme_id): u'deleted', 'flashes': [u'Meme deleted']})
        rv2 = self.client.get('/api/memes', follow_redirects=True)
        self.assertEquals(rv2.status_code, 200)
        self.assertEquals({u'memes': [], u'flashes': []}, json.loads(rv2.data))

    def test_search_memes(self):
        self.login()
        # add 3 memes to get us started
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        rv1 = self.client.post('/api/memes', data=dict( what=self.uri1, why=self.desc1),
            follow_redirects=True)
        rv2 = self.client.post('/api/memes', data=dict( what=self.uri2, why=self.desc2),
            follow_redirects=True)
        rv3 = self.client.get('/api/memes?q=description', follow_redirects=True)
        self.check_meme_json(rv3, self.uri0, self.desc0, last=False)
        self.check_meme_json(rv3, self.uri1, self.desc1, last=False)
        self.check_meme_json(rv3, self.uri2, self.desc2, last=False)
        rv4 = self.client.get('/api/memes?q=stuff', follow_redirects=True)
        self.check_meme_json(rv4, self.uri1, self.desc1, last=False)
        self.assertEqual(len(json.loads(rv4.data)['memes']), 1)
        rv5 = self.client.get('/api/memes?q=more', follow_redirects=True)
        self.check_meme_json(rv5, self.uri2, self.desc2, last=False)
        self.assertEqual(len(json.loads(rv5.data)['memes']), 1)
        rv6 = self.client.get('/api/memes?q=somewhere', follow_redirects=True)
        self.assertEqual(len(json.loads(rv6.data)['memes']), 2)

    def test_update_search(self):
        self.skipTest('Not implemented yet')

    def test_title_memes(self):
        self.login()
        rv = self.client.post('/api/memes', data=dict( what=self.title0, why=self.desc4,
        ), follow_redirects=True)
        self.check_meme_json(rv, self.title0, self.desc4)

    def test_update_fail(self):
        self.skipTest('Not implemented yet')

    def test_update_content(self):
        self.skipTest('Not implemented yet')
