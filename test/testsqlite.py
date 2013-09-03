from unittest import TestCase
from hactar import sqlite
from hactar.core import Nugget
import os

class TestSqlite(TestCase):
    def test_create(self):
        loc = 'test_create.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        one = sqlite.Sqlite(loc)
        two = sqlite.Sqlite(loc)
        self.assertEqual(one.loc, two.loc)
        os.remove(loc)

    def test_add_nugget(self):
        loc = 'test_add_nugget.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        backend = sqlite.Sqlite(loc)
        ngt = Nugget('Google, a great search engine.', 'http://www.google.com')
        backend.add_nugget(ngt)

