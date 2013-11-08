from unittest import TestCase
from datetime import date

from hactar import utils


class TestUtil(TestCase):

    def test_iso8601(self):
        func = utils.parse_iso8601
        self.assertEqual(func('2013'), (date(2013, 1, 1), date(2014, 1, 1)))
        self.assertEqual(func('1984'), (date(1984, 1, 1), date(1985, 1, 1)))
        self.assertEqual(func('4052'), (date(4052, 1, 1), date(4053, 1, 1)))
        self.assertEqual(func('2013-04'), (date(2013, 4, 1), date(2013, 5, 1)))
        self.assertEqual(func('2013-03'), (date(2013, 3, 1), date(2013, 4, 1)))
        self.assertEqual(func('2013-02'), (date(2013, 2, 1), date(2013, 3, 1)))
        self.assertEqual(func('2012-02'), (date(2012, 2, 1), date(2012, 3, 1)))
        self.assertEqual(func('2000-02'), (date(2000, 2, 1), date(2000, 3, 1)))
        self.assertEqual(func('2100-02'), (date(2100, 2, 1), date(2100, 3, 1)))
        self.assertEqual(func('2013-04-8'), (date(2013, 4, 8), date(2013, 4, 9)))
        self.assertEqual(func('2013-01-31'), (date(2013, 1, 31), date(2013, 2, 1)))
        self.assertEqual(func('2013-12-31'), (date(2013, 12, 31), date(2014, 1, 1)))
        self.assertRaises(ValueError, func, '2013-02-29')
        self.assertRaises(ValueError, func, '2013-hi-03')
        self.assertRaises(ValueError, func, '2013-13-03')
        self.assertRaises(ValueError, func, 'garbled')
        
