from unittest import TestCase
from datetime import date

from hactar import utils


class TestUtil(TestCase):

    def test_iso8601(self):
        func = utils.parse_iso8601
        self.assertEqual(func('2013'), (date(2013, 1, 1), 'year'))
        self.assertEqual(func('1984'), (date(1984, 1, 1), 'year'))
        self.assertEqual(func('4052'), (date(4052, 1, 1), 'year'))
        self.assertEqual(func('2013-04'), (date(2013, 4, 1), 'month'))
        self.assertEqual(func('2013-04-8'), (date(2013, 4, 8), 'day'))
        self.assertEqual(func('2013-04-8'), (date(2013, 4, 8), 'day'))
        self.assertRaises(ValueError, func, '2013-02-29')
        self.assertRaises(ValueError, func, '2013-hi-03')
        self.assertRaises(ValueError, func, '2013-13-03')
        self.assertRaises(ValueError, func, 'garbled')
        
