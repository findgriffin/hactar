
from hashlib import sha1
import shutil
import re
import json
import time
from dateutil.parser import parse
from datetime import datetime as dtime
from datetime import timedelta as tdelta

from flask.ext.testing import TestCase

from app import db, app
import hactar.models

class BaseTest(TestCase):

    _multiprocess_can_split = False


    def create_app(self):
        import json
        self.conf = json.load(open('config.json', 'rb'))['test']
        app.config.update(self.conf)
        self.idx = hactar.models.setup('test')
        app.logger.setLevel(30)
        app.celery_running = False
        return app

    def setUp(self):
        """Before each test, set up a blank database"""
        try:
            shutil.rmtree(self.conf['WHOOSH_BASE'])
        except OSError as err:
            pass
        hactar.models.setup('test')
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


class BaseMemeTest(BaseTest):

    uri0 = 'http://foobar.com'
    desc0 = 'a description of foobar'
    uri1 = 'http://stuff.com/somewhere'
    desc1 = 'a description of stuff'
    uri2 = 'http://more.com/somewhere'
    desc2 = 'a description of more'
    title0 = 'A title not a URI'
    desc4 = 'a description of this "not-URI"'

    def check_meme(self, resp, uri, desc, new=True, flash=None, isuri=True,
            logged_in=True):
        if flash:
            self.assertIn(flash, resp.data)
        elif new:
            msg = 'New meme was successfully added'
            self.assertIn(msg, resp.data)
        now = 'just now'
        self.assertEqual(resp.status_code, 200)
        meme_id = int(sha1(uri).hexdigest()[:15], 16)
        if logged_in:
            self.assertIn('<ahref="/memes/%s">(edit)</a>' % meme_id,
                    re.sub('\s+', '', resp.data))
        else:
            self.assertIn('<ahref="/memes/%s">(view)</a>' % meme_id,
                    re.sub('\s+', '', resp.data))
        if isuri:
            self.assertIn('<h4><a href="%s" target="_blank">%s</a>' % (uri, uri), resp.data)
        else:
            self.assertIn('<h4>%s' % uri, resp.data)
        self.assertIn('<p>%s</p>' % desc, resp.data)
        self.assertIn('%s</small></h4>' % now, resp.data)
        return meme_id

    def get_meme(self, rjson, meme_id):
        for meme in rjson['memes']:
            if int(meme['id']) == meme_id:
                return meme
        raise AssertionError('meme: %s not in response:%s' % (meme_id, rjson))

    def check_meme_json(self, resp, what, why, new=True, flash=None,
            last=True):
        rjson = json.loads(resp.data)
        isuri =  hactar.models.is_uri(what)
        if flash:
            self.assertEquals([flash], rjson['flashes'])
        elif last and new:
            msg = u'New meme was successfully added'
            self.assertEquals([msg], rjson['flashes'])
        self.assertEqual(resp.status_code, 200)
        meme_id = int(sha1(what).hexdigest()[:15], 16)
        if last:
            meme = rjson['memes'][0]
            self.assertEquals(meme_id, int(meme['id']))
        else:
            meme = self.get_meme(rjson, meme_id)
        self.assertEquals(len(meme.keys()), 9)
        self.assertEquals(what, meme['uri'] if isuri else meme['title'])
        self.assertEquals(why, meme['text'])
        now = int(time.time())
        added = parse(meme['added'])
        modified = parse(meme['modified'])
        if new:
            self.assertEquals(added, modified, 
                    msg='created / modified times are not equal %s' % meme)
        else:
            self.assertTrue(modified > added, 
                    msg='modified not later than added %s' % meme)
        return meme_id

class BaseActionTest(BaseTest):
    text0 = 'cool event'
    text1 = 'another fruity event'
    text2 = 'yet another event'

    def get_action(self, rjson, action_id):
        for action in rjson['actions']:
            if int(action['id']) == action_id:
                return action
        raise AssertionError('action: %s not in response:%s' % (action_id, rjson))

    def check_action_json(self, resp, text, new=True, flash=None,
            last=True):
        rjson = json.loads(resp.data)
        if flash:
            self.assertEquals([flash], rjson['flashes'])
        elif last is True and new:
            msg = u'New action was successfully added'
            self.assertEquals([msg], rjson['flashes'])
        self.assertEqual(resp.status_code, 200)
        # 1 is True evaluates to False, do it this way so we can pass in an int
        # in place of last=False when required.
        if last is True: # this 
            action_id = len(rjson['actions'])
            action = rjson['actions'][0]
            self.assertIsInstance(action, dict, msg='no action found in: %s' %
                    rjson)
            self.assertEqual(action_id, int(action['id']))
        elif type(last) == int:
            action_id = last
            action = self.get_action(rjson, action_id)
        else:
            raise ValueError('need an action_id or last=True')
        self.assertEquals(len(action.keys()), 9)
        self.assertEquals(text, action['text'])
        now = int(time.time())
        added = parse(action['added'])
        modified = parse(action['modified'])
        if new:
            self.assertEquals(added, modified, 
                    msg='created / modified times are not equal %s' % action)
        else:
            self.assertTrue(modified > added, 
                    msg='modified not later than added %s' % action)
        return action_id

    def check_action(self, resp, text, new=True, flash=None, logged_in=True):
        if flash:
            self.assertIn(flash, resp.data)
        elif new:
            msg = 'New action was successfully added'
            self.assertIn(msg, resp.data)
        now = 'just now'
        self.assertEqual(resp.status_code, 200)
        action_id = int(sha1(uri).hexdigest()[:15], 16)
        if logged_in:
            self.assertIn('<ahref="/actions/%s">(edit)</a>' % action_id,
                    re.sub('\s+', '', resp.data))
        else:
            self.assertIn('<ahref="/actions/%s">(view)</a>' % action_id,
                    re.sub('\s+', '', resp.data))
        if isuri:
            self.assertIn('<h4><a href="%s" target="_blank">%s</a>' % (uri, uri), resp.data)
        else:
            self.assertIn('<h4>%s' % uri, resp.data)
        self.assertIn('<p>%s</p>' % desc, resp.data)
        self.assertIn('%s</small></h4>' % now, resp.data)
        return action_id

def get_day(days=0):
    today = dtime.now()
    newday = today+tdelta(days=days)
    return newday
