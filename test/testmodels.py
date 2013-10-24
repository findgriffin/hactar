from unittest import TestCase
import logging

from hactar.models import Meme, Action, is_uri
from test.base import get_day

class TestMemeModel(TestCase):
    _multiprocess_can_split = True

    desc = 'a description here'
    uri0 = 'http://arthur.com'
    uri1 = 'arthur.com/link/to/stuff'
    title = 'A worthy title'

    def test_valid_uris(self):
        uri0 = 'http://arthur.com'
        uri1 = 'ftp://arthur.com'
        uri2 = 'ftp://arthur.com:9090'
        uri3 = 'ssh://arthur.com:22'
        self.assertTrue(is_uri(uri0), uri0)
        self.assertTrue(is_uri(uri1), uri1)
        self.assertTrue(is_uri(uri2), uri2)
        self.assertTrue(is_uri(uri3), uri3)

    def test_guessing_uris(self):
        uri0 = 'arthur.com/stuff/and/stuff'
        uri1 = 'arthur.com/STUFF/AND/HELLO/?q=hello'
        uri2 = 'arthur.com:80/stuff/and/stuff'
        uri3 = 'arthur.com'
        self.assertEquals(is_uri(uri0), 'http://'+uri0)
        self.assertEquals(is_uri(uri1), 'http://'+uri1)
        self.assertEquals(is_uri(uri2), None)
        self.assertEquals(is_uri(uri3), None)
        self.assertEquals(is_uri(self.uri1), 'http://'+self.uri1)

    def test_invalid_uris(self):
        self.assertFalse(is_uri('httparthur.com'))
        self.assertFalse(is_uri('httpar:thur.com'))
        self.assertFalse(is_uri('arthur.com'))
        self.assertFalse(is_uri('A worthy title'))

    def test_meme_uri(self):
        meme0 = Meme(self.desc, self.uri0)
        self.assertEqual(meme0.id, 518461505784485793L)
        self.assertEqual(meme0.sha1, '731f1fe19ff97a101945fa3b48039db508a71397')
        self.assertEqual(meme0.title, None)
        self.assertEqual(meme0.text, self.desc)
        self.assertEqual(meme0.uri, self.uri0)

    def test_meme_guess_uri(self):
        meme0 = Meme(self.desc, self.uri1)
        self.assertEqual(meme0.id, 439762162442543910L)
        self.assertEqual(meme0.sha1, '61a595b560ba3268e8006f81287456fbe957f3fc')
        self.assertEqual(meme0.title, None)
        self.assertEqual(meme0.uri, 'http://'+self.uri1)
        self.assertEqual(meme0.text, self.desc)

    def test_meme_errors(self):
        with self.assertRaises(ValueError):
            Meme('oneworddescription', 'http://arthur.com')
        with self.assertRaises(TypeError):
            Meme('nouriortitle')

    def test_meme_title(self):
        meme1 = Meme(self.desc, self.title)
        self.assertEqual(meme1.id, 614399577777769947L)
        self.assertEqual(meme1.sha1, '886c92927980ddbee13c129c1659cf70863de7d0')
        self.assertEqual(meme1.title, self.title)
        self.assertEqual(meme1.uri, None)
        self.assertEqual(meme1.text, self.desc)



class TestActionModel(TestCase):
    text = 'an action'

    def test_action_create(self):
        action0 = Action(self.text)
        self.assertEqual(action0.text, self.text)
        self.assertEqual(action0.due, None)
        self.assertEqual(action0.start_time, None)
        self.assertEqual(action0.finish_time, None)
        self.assertEqual(action0.is_task, False)
        self.assertEqual(action0.completed, None)
        self.assertEqual(action0.duration, None)
        self.assertEqual(action0.latent, None)
        self.assertEqual(action0.ongoing, None)

    def test_action_latent(self):
        due_date = get_day(1)
        action0 = Action(self.text, due=due_date)
        self.assertEqual(action0.text, self.text)
        self.assertEqual(action0.due, due_date)
        self.assertEqual(action0.start_time, None)
        self.assertEqual(action0.finish_time, None)
        self.assertEqual(action0.is_task, True)
        self.assertEqual(action0.completed, None)
        self.assertEqual(action0.duration, None)
        self.assertEqual(action0.latent, True)
        self.assertEqual(action0.ongoing, None)

    def test_action_ongoing(self):
        due_date = get_day(1)
        start_date = get_day()
        action0 = Action(self.text, due=due_date, start=start_date)
        self.assertEqual(action0.text, self.text)
        self.assertEqual(action0.due, due_date)
        self.assertEqual(action0.start_time, start_date)
        self.assertEqual(action0.finish_time, None)
        self.assertEqual(action0.is_task, True)
        self.assertEqual(action0.completed, None)
        self.assertEqual(action0.duration, None)
        self.assertEqual(action0.latent, False)
        self.assertEqual(action0.ongoing, True)
