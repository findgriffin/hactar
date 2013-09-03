from unittest import TestCase
from hactar import sqlite
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
