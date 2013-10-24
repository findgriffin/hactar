"""Tests for the hactar api"""
import json
from dateutil.parser import parse

from base import BaseMemeTest, BaseActionTest

class TestMemeApi(BaseMemeTest):

    # testing functions
    def test_empty_db(self):
        """Start with a blank database (via api)."""
        rv = self.client.get('/api/memes', follow_redirects=True)
        self.assertEquals(rv.status_code, 200)
        self.assertEquals({'memes': [], 'flashes': []}, json.loads(rv.data))

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
        extra =['four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
                'eleven', 'twelve', 'thirteen', 'fourteen'] 
        for num in extra:
            self.client.post('/api/memes', data=dict(what=num, why='meme %s' %
                num), follow_redirects=True)

        rv3 = self.client.get('/api/memes', follow_redirects=True)
        rjson = json.loads(rv3.data)
        self.assertEqual(len(rjson['memes']), 10)

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
        # try to delete it again
        rv4 = self.client.delete('/api/memes/%s' % meme_id, data=dict(
            delete='Delete'), follow_redirects=True)
        self.assertEquals(rv4.status_code, 404)

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
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme_json(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/api/memes/%s' % meme_id, data=dict(why=self.desc1),
                follow_redirects=True)
        rjson = json.loads(rv1.data)
        rjson_meme = rjson[unicode(meme_id)]
        self.assertEquals(rv1.status_code, 200)
        self.assertEquals(rjson['flashes'], [u'Meme successfully modified'])
        self.assertEquals(rjson_meme['uri'], self.uri0)
        self.assertEquals(rjson_meme['text'], self.desc1)
        self.assertEquals(rjson_meme['status_code'], u'-1')
        self.assertEquals(rjson_meme['id'], unicode(meme_id))
        modified = parse(rjson_meme['modified'])
        added = parse(rjson_meme['added'])
        self.assertTrue(modified > added)
        rv2 = self.client.get('/api/memes?q=stuff', follow_redirects=True )
        self.check_meme_json(rv2, self.uri0, self.desc1, last=False, new=False)

    def test_title_memes(self):
        self.login()
        rv = self.client.post('/api/memes', data=dict( what=self.title0, why=self.desc4,
        ), follow_redirects=True)
        self.check_meme_json(rv, self.title0, self.desc4)
        self.assertEquals(json.loads(rv.data)['memes'][0]['title'], self.title0)
        self.assertEquals(json.loads(rv.data)['memes'][0]['uri'], u'None')

    def test_update_fail(self):
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme_json(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/api/memes/%s' % (int(meme_id)-10), data=dict(why=self.desc1),
                follow_redirects=True)
        self.assertEquals(rv1.status_code, 404)

    def test_update_content(self):
        """Check that we can update the content of a meme (with api)"""
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme_json(rv0, self.uri0, self.desc0, new=True)
        content = 'page content'
        title = 'super duper title'
        rv1 = self.client.post('/api/memes/%s' % meme_id,
                data=dict(content=content, title=title, status_code=200),
                follow_redirects=True)
        self.assertEquals(rv1.status_code, 200)
        rjson = json.loads(rv1.data)
        rjson_meme = rjson[unicode(meme_id)]
        self.assertEquals(rjson['flashes'], [u'Meme successfully modified'])
        self.assertEquals(rjson_meme['title'], title)
        self.assertEquals(rjson_meme['content'], content)
        self.assertEquals(rjson_meme['status_code'], u'200')
        checked = parse(rjson_meme['checked'])
        added = parse(rjson_meme['added'])
        self.assertTrue(checked > added)
        rv2 = self.client.get('/api/memes?q=duper', follow_redirects=True)
        self.check_meme_json(rv2, self.uri0, self.desc0, last=False)

class TestActionApi(BaseActionTest):

    # testing functions
    def test_empty_db(self):
        """Start with a blank database (via api)."""
        rv = self.client.get('/api/actions', follow_redirects=True)
        self.assertEquals(rv.status_code, 200)
        self.assertEquals({'actions': [], 'flashes': []}, json.loads(rv.data))

    def test_add_action(self):
        """Test adding actions (with api)"""
        self.login()
        rv0 = self.client.post('/api/actions', data=dict(what=self.text0), 
                follow_redirects=True)
        self.check_action_json(rv0, self.text0)
        rv1 = self.client.post('/api/actions', data=dict( what=self.text1,
        ), follow_redirects=True)
        self.check_action_json(rv1, self.text0, new=True, last=1)
        self.check_action_json(rv1, self.text1)
        rv2 = self.client.post('/api/actions', data=dict( what=self.text2,
        ), follow_redirects=True)
        self.check_action_json(rv2, self.text0, new=True, last=1)
        self.check_action_json(rv2, self.text1, new=True, last=2)
        self.check_action_json(rv2, self.text2)
        extra =['four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'
                'eleven', 'twelve', 'thirteen', 'fourteen'] 
        for num in extra:
            self.client.post('/api/actions', data=dict(what='event %s' % num), 
                    follow_redirects=True)
        rv3 = self.client.get('/api/actions', follow_redirects=True)
        rjson = json.loads(rv3.data)
        self.assertEqual(len(rjson['actions']), 10)

    def test_delete(self):
        """Test deleting a action (with api)"""
        self.login()
        rv0 = self.client.post('/api/actions', data=dict(what=self.text0), 
                follow_redirects=True)
        action_id = self.check_action_json(rv0, self.text0)
        rv1 = self.client.delete('/api/actions/%s' % action_id)
        self.assertEquals(rv1.status_code, 200)
        self.assertEquals(json.loads(rv1.data), 
                {unicode(action_id): u'deleted', 'flashes': [u'action deleted']})
        rv2 = self.client.get('/api/actions', follow_redirects=True)
        self.assertEquals(rv2.status_code, 200)
        self.assertEquals({u'actions': [], u'flashes': []}, json.loads(rv2.data))
        # try to delete it again
        rv4 = self.client.delete('/api/actions/%s' % action_id, data=dict(
            delete='Delete'), follow_redirects=True)
        self.assertEquals(rv4.status_code, 404)

    def test_search(self):
        self.login()
        # add 3 actions to get us started
        rv0 = self.client.post('/api/actions', data=dict( what=self.text0),
            follow_redirects=True)
        rv1 = self.client.post('/api/actions', data=dict( what=self.text1),
            follow_redirects=True)
        rv2 = self.client.post('/api/actions', data=dict( what=self.text2),
            follow_redirects=True)
        rv3 = self.client.get('/api/actions?q=event', follow_redirects=True)
        self.check_action_json(rv3, self.text0, last=1)
        self.check_action_json(rv3, self.text1, last=2)
        self.check_action_json(rv3, self.text2, last=3)
        rv4 = self.client.get('/api/actions?q=cool', follow_redirects=True)
        self.check_action_json(rv4, self.text0, last=1)
        self.assertEqual(len(json.loads(rv4.data)['actions']), 1)
        rv5 = self.client.get('/api/actions?q=fruity', follow_redirects=True)
        self.check_action_json(rv5, self.text1, last=2)
        self.assertEqual(len(json.loads(rv5.data)['actions']), 1)
        rv6 = self.client.get('/api/actions?q=another', follow_redirects=True)
        self.assertEqual(len(json.loads(rv6.data)['actions']), 2)

    def test_update_search(self):
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme_json(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/api/memes/%s' % meme_id, data=dict(why=self.desc1),
                follow_redirects=True)
        rjson = json.loads(rv1.data)
        rjson_meme = rjson[unicode(meme_id)]
        self.assertEquals(rv1.status_code, 200)
        self.assertEquals(rjson['flashes'], [u'Meme successfully modified'])
        self.assertEquals(rjson_meme['uri'], self.uri0)
        self.assertEquals(rjson_meme['text'], self.desc1)
        self.assertEquals(rjson_meme['status_code'], u'-1')
        self.assertEquals(rjson_meme['id'], unicode(meme_id))
        modified = parse(rjson_meme['modified'])
        added = parse(rjson_meme['added'])
        self.assertTrue(modified > added)
        rv2 = self.client.get('/api/memes?q=stuff', follow_redirects=True )
        self.check_meme_json(rv2, self.uri0, self.desc1, last=False, new=False)

    def test_title_memes(self):
        self.login()
        rv = self.client.post('/api/memes', data=dict( what=self.title0, why=self.desc4,
        ), follow_redirects=True)
        self.check_meme_json(rv, self.title0, self.desc4)
        self.assertEquals(json.loads(rv.data)['memes'][0]['title'], self.title0)
        self.assertEquals(json.loads(rv.data)['memes'][0]['uri'], u'None')

    def test_update_fail(self):
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme_json(rv0, self.uri0, self.desc0)
        rv1 = self.client.post('/api/memes/%s' % (int(meme_id)-10), data=dict(why=self.desc1),
                follow_redirects=True)
        self.assertEquals(rv1.status_code, 404)

    def test_update_content(self):
        """Check that we can update the content of a meme (with api)"""
        self.login()
        rv0 = self.client.post('/api/memes', data=dict( what=self.uri0, why=self.desc0),
            follow_redirects=True)
        meme_id = self.check_meme_json(rv0, self.uri0, self.desc0, new=True)
        content = 'page content'
        title = 'super duper title'
        rv1 = self.client.post('/api/memes/%s' % meme_id,
                data=dict(content=content, title=title, status_code=200),
                follow_redirects=True)
        self.assertEquals(rv1.status_code, 200)
        rjson = json.loads(rv1.data)
        rjson_meme = rjson[unicode(meme_id)]
        self.assertEquals(rjson['flashes'], [u'Meme successfully modified'])
        self.assertEquals(rjson_meme['title'], title)
        self.assertEquals(rjson_meme['content'], content)
        self.assertEquals(rjson_meme['status_code'], u'200')
        checked = parse(rjson_meme['checked'])
        added = parse(rjson_meme['added'])
        self.assertTrue(checked > added)
        rv2 = self.client.get('/api/memes?q=duper', follow_redirects=True)
        self.check_meme_json(rv2, self.uri0, self.desc0, last=False)
