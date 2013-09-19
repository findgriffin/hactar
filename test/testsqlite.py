from unittest import TestCase
from hactar import sqlite
from hactar.core import Nugget
from hactar.core import User
from sqlite3 import IntegrityError
import os

class TestSqlite(TestCase):

    def test_create(self):
        """Create sqlite database"""
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
        """Add nugget to database"""
        loc = 'test/add_nugget.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        backend = sqlite.Sqlite(loc)
        ngt = Nugget('Google, a great search engine.', 'http://www.google.com')
        backend.add_nugget(ngt)

    def test_create_fail(self):
        """Fail for nonexistant db"""
        loc = 'test/create_fail.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        with self.assertRaises(ValueError):
            sqlite.Sqlite(loc, create=False)

    def test_add_identical_nuggets(self):
        """Add identical nuggets"""
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
        """Add multiple nuggets"""
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
        """Test db persistence"""
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

    def test_search_single(self):
        """search for single keyword"""
        loc = 'test/test_create.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        bck_one = sqlite.Sqlite(loc, create=True)
        usr = User('funnyman', bck_one)
        ngt1 = ('foo world', 'http://www.fooworld.com')
        ngt2 = ('bar world', 'http://www.barworld.com')
        ngt3 = ('baz world', 'http://www.bazworld.com')
        ngt4 = ('foo face', 'http://www.fooface.com')
        ngt5 = ('bar face', 'http://www.barface.com')
        ngt6 = ('baz face', 'http://www.bazface.com')
        usr.add_nugget(*ngt1)
        usr.add_nugget(*ngt2)
        usr.add_nugget(*ngt3)
        usr.add_nugget(*ngt4)
        usr.add_nugget(*ngt5)
        usr.add_nugget(*ngt6)
        ngts = usr.get_nuggets(['world'])
        self.assertEqual(len(ngts), 3)
        ngts_simple = [(str(i[5]), str(i[2])) for i in ngts]
        for ngt in [ngt1, ngt2, ngt3]:
            self.assertIn(ngt, ngts_simple)
        os.remove(loc)

    def test_search_noresults(self):
        """Search with no results"""
        loc = 'test/test_create.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        bck_one = sqlite.Sqlite(loc, create=True)
        usr = User('funnyman', bck_one)
        ngt1 = ('foo world', 'http://www.fooworld.com')
        ngt2 = ('bar world', 'http://www.barworld.com')
        ngt3 = ('baz world', 'http://www.bazworld.com')
        ngt4 = ('foo face', 'http://www.fooface.com')
        ngt5 = ('bar face', 'http://www.barface.com')
        ngt6 = ('baz face', 'http://www.bazface.com')
        usr.add_nugget(*ngt1)
        usr.add_nugget(*ngt2)
        usr.add_nugget(*ngt3)
        usr.add_nugget(*ngt4)
        usr.add_nugget(*ngt5)
        usr.add_nugget(*ngt6)
        ngts = usr.get_nuggets(['hello'])
        self.assertEqual(len(ngts), 0)
        os.remove(loc)

    def test_search_multiple(self):
        """Search with multiple results"""
        loc = 'test/test_create.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        bck_one = sqlite.Sqlite(loc, create=True)
        usr = User('funnyman', bck_one)
        ngt1 = ('foo world', 'http://www.fooworld.com')
        ngt2 = ('bar world', 'http://www.barworld.com')
        ngt3 = ('baz world', 'http://www.bazworld.com')
        ngt4 = ('foo face', 'http://www.fooface.com')
        ngt5 = ('bar face', 'http://www.barface.com')
        ngt6 = ('baz face', 'http://www.bazface.com')
        usr.add_nugget(*ngt1)
        usr.add_nugget(*ngt2)
        usr.add_nugget(*ngt3)
        usr.add_nugget(*ngt4)
        usr.add_nugget(*ngt5)
        usr.add_nugget(*ngt6)
        ngts = usr.get_nuggets(['foo', 'baz'])
        self.assertEqual(len(ngts), 4)
        ngts_simple = [(str(i[5]), str(i[2])) for i in ngts]
        for ngt in [ngt1, ngt3, ngt4, ngt6]:
            self.assertIn(ngt, ngts_simple)
        os.remove(loc)
