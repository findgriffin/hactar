import os
from unittest import TestCase

from hactar.core import Plugins
from hactar.core import User
from hactar.sqlite import Sqlite

class TestPlugins(TestCase):

    def test_initialise(self):
        plugins = Plugins()
        self.assertEqual(len(plugins.nugget['create']), 1 )
        self.assertEqual(len(plugins.nugget['update']), 1 )
        self.assertEqual(len(plugins.nugget['delete']), 1 )
        self.assertTrue(hasattr(plugins.nugget['create'][0], '__call__'))
        self.assertTrue(hasattr(plugins.nugget['update'][0], '__call__'))
        self.assertTrue(hasattr(plugins.nugget['delete'][0], '__call__'))
        self.assertEqual(len(plugins.task['create']), 0 )
        self.assertEqual(len(plugins.task['update']), 0 )
        self.assertEqual(len(plugins.task['delete']), 0 )
        self.assertEqual(len(plugins.user['create']), 0 )
        self.assertEqual(len(plugins.user['update']), 0 )
        self.assertEqual(len(plugins.user['delete']), 0 )

    def test_nugget_create(self):
        loc = 'test/basic_add_nugget.sqlite'
        try:
            os.remove(loc)
        except OSError:
            pass
        backend = Sqlite(loc)
        usr = User('dave', backend)
        usr.add_nugget('Google, a great search engine.', 'http://www.google.com')
        self.assertTrue(usr.just_added.scraped)
