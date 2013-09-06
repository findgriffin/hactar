from unittest import TestCase
from hactar import core

class TestPlugins(TestCase):

    def test_initialise(self):
        self.assertEqual(core.plugins, 'hello')

