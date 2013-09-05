import os
from unittest import TestCase

from hactar.core import User
from hactar.core import Nugget
from hactar.core import Task
from hactar.backend import Backend
from hactar.sqlite import Sqlite

class TestTask(TestCase):

    def test_create_task(self):
        tsk = Task('do something')
        self.assertEqual(tsk.text, 'do something')

class TestUser(TestCase):

    def test_create_user(self):
        backend = Backend()
        usr = User('dave', backend)
        self.assertEqual(usr.name, 'dave')
        self.assertEqual(usr.backend, backend)

    def test_add_nugget(self):
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
        ngt = Nugget('Google, a great search engine.', 'http://www.google.com')
        self.assertEqual(ngt.sha1, '738ddf35b3a85a7a6ba7b232bd3d5f1e4d284ad1')

    def test_bad_uri(self):
        with self.assertRaises(ValueError) as err:
            Nugget('Google, a great search engine.', 'www.google.com')
        self.assertTrue(err.exception.message.startswith('URI:'))

    def test_bad_description(self):
        with self.assertRaises(ValueError) as err:
            Nugget('Google,', 'http://www.google.com')
        self.assertTrue(err.exception.message.startswith('description'))

