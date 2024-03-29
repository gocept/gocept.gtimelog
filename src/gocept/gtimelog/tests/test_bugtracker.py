# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.gtimelog.bugtracker
import gocept.gtimelog.core
import gocept.gtimelog.util
import unittest


class DummyWindow(gocept.gtimelog.core.TimeWindow):

    def __init__(self):
        self.items = []
        self.virtual_midnight = datetime.time(2, 0)

    def add(self, timestamp, entry):
        self.items.append(
            (gocept.gtimelog.util.parse_datetime(timestamp), entry))
        self.min_timestamp = self.items[0][0]
        self.max_timestamp = self.items[-1][0]


class ConvertTimelogTest(unittest.TestCase):

    def convert(self, window):
        settings = type('Dummy', (object,), {})()
        settings.redmines = []
        settings.disabled_trackers = []
        trackers = gocept.gtimelog.bugtracker.Bugtrackers(settings)
        return list(trackers._timelog_to_issues(window))

    def test_no_issue_referenced_should_not_show(self):
        window = DummyWindow()
        window.add('2009-08-01 08:00', 'arrived')
        window.add('2009-08-01 10:00', 'Operations: General activities: Email')
        entries = self.convert(window)
        self.assertEqual([], entries)

    def test_issue_reference_should_be_found_anywhere(self):
        window = DummyWindow()
        window.add('2009-08-01 08:00', 'arrived')
        window.add('2009-08-01 10:00', 'Operations: Programming: #123: foo')
        window.add('2009-08-01 10:15', '#2: foo')
        window.add('2009-08-01 10:45', 'foo bar (#34)')
        entries = self.convert(window)
        self.assertEqual(3, len(entries))
        self.assertEqual(123, entries[0].issue)
        self.assertEqual(0.25, entries[1].duration)
        self.assertEqual('foo bar (#34)', entries[2].comment)

    def test_multiple_entries_same_issue_should_be_combined(self):
        window = DummyWindow()
        window.add('2009-08-01 08:00', 'arrived')
        window.add('2009-08-01 10:00', 'Operations: Programming: #123: foo')
        window.add('2009-08-01 10:15', '#123: foo')
        window.add('2009-08-02 08:00', 'arrived')
        window.add('2009-08-02 09:00', '#123: bar')
        entries = self.convert(window)
        self.assertEqual(2, len(entries))
        self.assertEqual(2.25, entries[0].duration)
        self.assertEqual('#123: foo', entries[0].comment)
        self.assertEqual(1, entries[1].duration)

    def test_extract_project_from_comment(self):
        window = DummyWindow()
        window.add('2009-08-01 08:00', 'arrived')
        window.add('2009-08-01 10:00', 'Operations: Programming: #123: foo')
        window.add('2009-08-01 10:15', '#2: foo')
        window.add('2009-08-01 10:45', 'foo bar (#34)')
        entries = self.convert(window)
        self.assertEqual(3, len(entries))
        self.assertEqual('Operations', entries[0].project)
        self.assertEqual(None, entries[1].project)
        self.assertEqual(None, entries[2].project)


class ParseCommentTest(unittest.TestCase):

    def setUp(self):
        self.entry = gocept.gtimelog.bugtracker.TimelogEntry(
            datetime.datetime(2011, 5, 4, 3, 2), None, None, '')

    def test_project_activity_issue_comment(self):
        self.entry.add_comment('Operations: Programming: #123: foo bar')
        self.assertEqual('#123: foo bar', self.entry.comment)
        self.entry.add_comment('Operations: Programming: #123: baz qux')
        self.assertEqual('#123: foo bar, #123: baz qux', self.entry.comment)

    def test_project_activity_issue_no_colon_comment(self):
        self.entry.add_comment('Operations: Programming: #123 foo bar')
        self.assertEqual('#123 foo bar', self.entry.comment)
        self.entry.add_comment('Operations: Programming: #123 baz qux')
        self.assertEqual('#123 foo bar, #123 baz qux', self.entry.comment)

    def test_no_project(self):
        self.entry.add_comment('#123: foo')
        self.assertEqual('#123: foo', self.entry.comment)
        self.entry.add_comment('#123: bar')
        self.assertEqual('#123: foo, #123: bar', self.entry.comment)

    def test_no_issue(self):
        self.entry.add_comment('Operations: Programming: foo')
        self.assertEqual('foo', self.entry.comment)
        self.entry.add_comment('Operations: Programming: bar')
        self.assertEqual('foo, bar', self.entry.comment)

    def test_no_duplicate_comments(self):
        self.entry.add_comment('Operations: Programming: foo')
        self.assertEqual('foo', self.entry.comment)
        self.entry.add_comment('Operations: Programming: foo')
        self.assertEqual('foo', self.entry.comment)
        self.entry.add_comment('Operations: Programming: bar')
        self.assertEqual('foo, bar', self.entry.comment)

    def test_comments_max_length(self):
        self.entry.add_comment('foo')
        self.assertEqual('foo', self.entry.comment)
        self.entry.add_comment(256*'x')
        self.assertEqual('foo, '+250*'x', self.entry.comment)


class Settings(object):
    pass


class Tracker(dict):

    def __init__(self, **kw):
        self.update(api_key='', activity='', username='', password='')
        self.update(kw)


class FindTrackerTest(unittest.TestCase):

    def test_tracker_with_longest_prefix_match_gets_project(self):
        settings = type('Dummy', (object,), {})()
        settings.redmines = [
            Tracker(url='http://1', projects=['as', 'bsdf']),
            Tracker(url='http://2', projects=['asdfg']),
            Tracker(url='http://4', projects=['asdf']),
            Tracker(url='http://5', projects=['d', 'asdf_']),
            Tracker(url='http://6', projects=['asdf', 'e']),
        ]
        settings.disabled_trackers = [
            Tracker(url='http://3', projects=['asdf', 'b', 'c']),
        ]
        bugtrackers = gocept.gtimelog.bugtracker.Bugtrackers(settings)
        self.assertEqual('http://5', bugtrackers.find_tracker('asdf_g').url)
        self.assertEqual('http://1', bugtrackers.find_tracker('AS_DF').url)
        # disabled tracker
        self.assertIsNone(bugtrackers.find_tracker('bbsdf').url)
