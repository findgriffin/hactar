from unittest import TestCase
from hactar import sqlite
from hactar.core import Nugget
from hactar.core import User
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
        ngt0 = Nugget('foo is great', 'http://www.foo.com')
        ngt1 = Nugget('foo is awesome', 'http://www.foo.com')
        backend.add_nugget(ngt0)
        with self.assertRaises(IntegrityError):
            backend.add_nugget(ngt1)

    def test_add_multiple_nuggets(self):
        loc = 'test/add_multiple_nuggets.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        backend = sqlite.Sqlite(loc)
        ngt0 = Nugget('foo is great', 'http://www.foo.com')
        ngt1 = Nugget('bar is awesome', 'http://www.bar.com')
        backend.add_nugget(ngt0)
        backend.add_nugget(ngt1)
        ngts = backend.get_nuggets()
        self.assertEqual(len(ngts), 2)


    def test_persistence(self):
        loc = 'test/test_create.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        bck_one = sqlite.Sqlite(loc, create=True)
        usr_one = User('funnyman', bck_one)
        usr_one.add_nugget('foo world', 'http://www.foo.com')
        bck_two = sqlite.Sqlite(loc, create=False)
        usr_two = User('funnyman', bck_two)
        ngts = usr_two.get_nuggets()
        self.assertEqual(len(ngts), 1)
        os.remove(loc)
