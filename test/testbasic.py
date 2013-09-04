from unittest import TestCase

from hactar.core import User
from hactar.core import Nugget
from hactar.core import Task
from hactar.backend import Backend

class TestBasic(TestCase):

    def test_create_nugget(self):
        ngt = Nugget('Google, a great search engine.', 'http://www.google.com')
        self.assertEqual(ngt.sha1, '738ddf35b3a85a7a6ba7b232bd3d5f1e4d284ad1')

    def test_create_task(self):
        tsk = Task('do something')
        self.assertEqual(tsk.text, 'do something')

    def test_create_user(self):
        backend = Backend()
        usr = User('dave', backend)
        self.assertEqual(usr.name, 'dave')
        self.assertEqual(usr.backend, backend)

