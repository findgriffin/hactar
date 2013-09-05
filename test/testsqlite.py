from unittest import TestCase
from hactar import sqlite
from hactar.core import Nugget
from sqlite3 import IntegrityError
import os

class TestSqlite(TestCase):

    def test_create(self):
        loc = 'test/test_create.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        one = sqlite.Sqlite(loc, create=True)
        two = sqlite.Sqlite(loc, create=False)
        self.assertEqual(one.loc, two.loc)
        os.remove(loc)

    def test_add_nugget(self):
        loc = 'test/add_nugget.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        backend = sqlite.Sqlite(loc)
        ngt = Nugget('Google, a great search engine.', 'http://www.google.com')
        backend.add_nugget(ngt)

    def test_create_fail(self):
        loc = 'test/create_fail.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        with self.assertRaises(ValueError):
            sqlite.Sqlite(loc, create=False)

    def test_add_identical_nuggets(self):
        loc = 'test/add_identical_nuggets.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        backend = sqlite.Sqlite(loc)
        ngt = Nugget('Google, a great search engine.', 'http://www.google.com')
        backend.add_nugget(ngt)
        with self.assertRaises(IntegrityError):
            backend.add_nugget(ngt)

    def test_add_multiple_nuggets(self):
        loc = 'test/add_multiple_nuggets.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        backend = sqlite.Sqlite(loc)
        ngt = Nugget('Google, a great search engine.', 'http://www.google.com')
        backend.add_nugget(ngt)
        with self.assertRaises(IntegrityError):
            backend.add_nugget(ngt)

