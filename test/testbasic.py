import os
from unittest import TestCase

from hactar.core import User
from hactar.core import Nugget
from hactar.core import Task
from hactar.backend import Backend
from hactar.sqlite import Sqlite

class TestTask(TestCase):

    def test_create_task(self):
        """Create a task"""
        tsk = Task('do something')
        self.assertEqual(tsk.text, 'do something')

class TestUser(TestCase):

    def test_create_user(self):
        """Create a user"""
        backend = Backend('x-marks-the-spot')
        usr = User('dave', backend)
        self.assertEqual(usr.name, 'dave')
        self.assertEqual(usr.backend, backend)

    def test_add_nugget(self):
        """Add a nugget to user"""
        loc = 'test/basic_add_nugget.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        backend = Sqlite(loc)
        usr = User('dave', backend)
        usr.add_nugget('Google, a great search engine.', 'http://www.google.com')
        nuggets = usr.get_nuggets()
        self.assertEqual(len(nuggets), 1)

class TestNugget(TestCase):

    def test_create(self):
        """Create a nugget"""
        ngt = Nugget('Google, a great search engine.', 'http://www.google.com')
        self.assertEqual(ngt.sha1, '738ddf35b3a85a7a6ba7b232bd3d5f1e4d284ad1')

    def test_bad_uri(self):
        """Add nugget with bad URI"""
        with self.assertRaises(ValueError) as err:
            Nugget('Google, a great search engine.', 'www.google.com')
        self.assertTrue(err.exception.message.startswith('URI:'))

    def test_bad_description(self):
        """Add nugget with one word description"""
        with self.assertRaises(ValueError) as err:
            Nugget('Google,', 'http://www.google.com')
        self.assertTrue(err.exception.message.startswith('Description'))

    def test_desc_only(self):
        """Add nugget with no URI"""
        ngt = Nugget('Cricket is not cool.')
        self.assertEqual(ngt.sha1, 'e5f54f60323ee882c1dedda2540f2a58fb2acf3b')

    def test_index(self):
        """Add nugget, check keywords."""
        ngt = Nugget('Cricket is not cool.')
        ngt.create_index()
        keywords = ngt.keywords
        self.assertEqual(len(keywords), 4)
        self.assertIn('cricket', keywords)
        self.assertIn('is', keywords)
        self.assertIn('not', keywords)
        self.assertIn('cool', keywords)

