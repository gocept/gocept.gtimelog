# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
import StringIO
from gocept.gtimelog.util import (
    format_duration, format_duration_short, format_duration_long,
    parse_datetime, parse_time, virtual_day, different_days, uniq)
from gocept.gtimelog.core import TimeWindow
from datetime import timedelta, datetime, date, time


class UtilityFunctions(unittest.TestCase):

    def test_format_duration(self):
        self.assertEqual(' 0 h  0 min', format_duration(timedelta(0)))
        self.assertEqual(' 0 h  1 min', format_duration(timedelta(minutes=1)))
        self.assertEqual(' 1 h  0 min', format_duration(timedelta(minutes=60)))

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
        output = StringIO.StringIO()
        timewindow.weekly_report(output,
                                    "somebody@example.com",
                                    "Somebody")
        self.assertIn("No work done this week.", output.getvalue())
