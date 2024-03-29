# Copyright (c) 2012,2019 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from gocept.gtimelog.core import TimeWindow
from gocept.gtimelog.util import different_days
from gocept.gtimelog.util import format_duration
from gocept.gtimelog.util import format_duration_long
from gocept.gtimelog.util import format_duration_short
from gocept.gtimelog.util import parse_date
from gocept.gtimelog.util import parse_datetime
from gocept.gtimelog.util import parse_time
from gocept.gtimelog.util import uniq
from gocept.gtimelog.util import virtual_day
from io import StringIO
import unittest


class UtilityFunctions(unittest.TestCase):

    def test_format_duration(self):
        self.assertEqual(' 0 h  0 min', format_duration(timedelta(0)))
        self.assertEqual(' 0 h  1 min', format_duration(timedelta(minutes=1)))
        self.assertEqual(' 1 h  0 min', format_duration(timedelta(minutes=60)))
        self.assertEqual('-42 h 19 min', format_duration(
            timedelta(seconds=-152340)))
        self.assertEqual('42 h 19 min', format_duration(
            timedelta(seconds=152340)))

    def test_format_short(self):
        self.assertEqual(' 0:00', format_duration_short(timedelta(0)))
        self.assertEqual(' 0:01', format_duration_short(timedelta(minutes=1)))
        self.assertEqual(' 0:59', format_duration_short(timedelta(minutes=59)))
        self.assertEqual(' 1:00', format_duration_short(timedelta(minutes=60)))
        self.assertEqual('26:03', format_duration_short(
            timedelta(days=1, hours=2, minutes=3)))

    def test_format_duration_long(self):
        self.assertEqual(' 0 min', format_duration_long(timedelta(0)))
        self.assertEqual(' 1 min', format_duration_long(timedelta(minutes=1)))
        self.assertEqual(' 1 hour ', format_duration_long(
            timedelta(minutes=60)))
        self.assertEqual(' 1 hour   5 min', format_duration_long(
            timedelta(minutes=65)))
        self.assertEqual(' 2 hours', format_duration_long(timedelta(hours=2)))
        self.assertEqual(' 2 hours  1 min', format_duration_long(
            timedelta(hours=2, minutes=1)))
        self.assertEqual('12 hours 32 min', format_duration_long(
            timedelta(hours=12, minutes=32)))

    def test_parse_datetime(self):
        self.assertEqual(datetime(2005, 2, 3, 2, 13),
                         parse_datetime('2005-02-03 02:13'))
        self.assertRaises(ValueError, lambda: parse_datetime('xyzzy'))

    def test_parse_date(self):
        self.assertEqual(date(2021, 8, 25), parse_date('2021-08-25'))
        self.assertRaises(ValueError, lambda: parse_date('2021-08-25 10:00'))
        self.assertRaises(ValueError, lambda: parse_date('2021-08'))
        self.assertRaises(ValueError, lambda: parse_date('25.08.2021'))
        self.assertRaises(ValueError, lambda: parse_date('xyzzy'))

    def test_parse_time(self):
        self.assertEqual(time(2, 13), parse_time('02:13'))
        self.assertRaises(ValueError, lambda: parse_time('xyzzy'))

    def test_virtual_day(self):
        vm = time(2, 0)
        self.assertEqual(date(2005, 2, 2),
                         virtual_day(datetime(2005, 2, 3, 1, 15), vm))
        self.assertEqual(date(2005, 2, 2),
                         virtual_day(datetime(2005, 2, 3, 1, 59), vm))
        self.assertEqual(date(2005, 2, 3),
                         virtual_day(datetime(2005, 2, 3, 2, 0), vm))
        self.assertEqual(date(2005, 2, 3),
                         virtual_day(datetime(2005, 2, 3, 12, 0), vm))
        self.assertEqual(date(2005, 2, 3),
                         virtual_day(datetime(2005, 2, 3, 23, 59), vm))

    def test_different_days(self):
        vm = time(2, 0)
        self.assertTrue(different_days(
            datetime(2005, 2, 3, 1, 15),
            datetime(2005, 2, 3, 2, 15), vm))
        self.assertFalse(different_days(
            datetime(2005, 2, 3, 11, 15),
            datetime(2005, 2, 3, 12, 15), vm))

    def test_uniq(self):
        self.assertEqual(
            ['a', 'b', 'c', 'd', 'b', 'd'],
            uniq(['a', 'b', 'b', 'c', 'd', 'b', 'd']))
        self.assertEqual(['a'], uniq(['a']))
        self.assertEqual([], uniq([]))

    def test_weekly_report(self):
        timewindow = TimeWindow("", datetime(2005, 2, 3, 1, 15),
                                datetime(2005, 2, 3, 2, 15), time(2, 0))
        output = StringIO()
        timewindow.weekly_report(output,
                                 "somebody@example.com",
                                 "Somebody")
        self.assertIn("No work done this week.", output.getvalue())
