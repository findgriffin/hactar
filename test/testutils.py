from unittest import TestCase
from datetime import datetime as dtime

from hactar import utils


class TestUtil(TestCase):

    def test_iso8601(self):
        func = utils.parse_iso8601
        self.assertEqual(func('2013'), get_days(2013, 1, 1, 2013, 12, 31))
        self.assertEqual(func('1984'), get_days(1984, 1, 1, 1984, 12, 31))
        self.assertEqual(func('4052'), get_days(4052, 1, 1, 4052, 12, 31))
        self.assertEqual(func('2013-04'), get_days(2013, 4, 1, 2013, 4, 30))
        self.assertEqual(func('2013-03'), get_days(2013, 3, 1, 2013, 3, 31))
        self.assertEqual(func('2013-02'), get_days(2013, 2, 1, 2013, 2, 28))
        self.assertEqual(func('2012-02'), get_days(2012, 2, 1, 2012, 2, 29))
        self.assertEqual(func('2000-02'), get_days(2000, 2, 1, 2000, 2, 29))
        self.assertEqual(func('2100-02'), get_days(2100, 2, 1, 2100, 2, 28))
        self.assertEqual(func('2013-04-8'), get_days(2013, 4, 8, 2013, 4, 8))
        self.assertEqual(func('2013-01-31'), get_days(2013, 1, 31, 2013, 1, 31))
        self.assertEqual(func('2013-12-31'), get_days(2013, 12, 31, 2013, 12, 31))
        self.assertRaises(ValueError, func, '2013-02-29')
        self.assertRaises(ValueError, func, '2013-hi-03')
        self.assertRaises(ValueError, func, '2013-13-03')
        self.assertRaises(ValueError, func, 'garbled')
        

def get_days(f_year, f_month, f_day, l_year, l_month, l_day):
    f_time = dtime(f_year, f_month, f_day, 0, 0)
    l_time = dtime(l_year, l_month, l_day, 23, 59, 59, 999999)
    return (f_time, l_time)
