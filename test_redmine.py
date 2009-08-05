from redmine import timelog_to_issues as convert
import datetime
import gtimelog
import tempfile
import unittest


class TestWindow(gtimelog.TimeWindow):

    def __init__(self):
        self.items = []
        self.virtual_midnight = datetime.time(2, 0)

    def add(self, timestamp, entry):
        self.items.append((gtimelog.parse_datetime(timestamp), entry))
        self.min_timestamp = self.items[0][0]
        self.max_timestamp = self.items[-1][0]


class ConvertTimelogTest(unittest.TestCase):

    def test_no_issue_referenced_should_not_show(self):
        window = TestWindow()
        window.add('2009-08-01 08:00', 'arrived')
        window.add('2009-08-01 10:00', 'Operations: General activities: Email')
        entries = convert(window)
        self.assertEqual([], entries)

    def test_issue_reference_should_be_found_anywhere(self):
        window = TestWindow()
        window.add('2009-08-01 08:00', 'arrived')
        window.add('2009-08-01 10:00', 'Operations: Programming: #123: foo')
        window.add('2009-08-01 10:15', '#2: foo')
        window.add('2009-08-01 10:45', 'foo bar (#34)')
        entries = convert(window)
        self.assertEqual(3, len(entries))
        self.assertEqual('123', entries[0].issue)
        self.assertEqual(0.25, entries[1].duration)
        self.assertEqual('foo bar (#34)', entries[2].comment)

    def test_multiple_entries_same_issue_should_be_combined(self):
        window = TestWindow()
        window.add('2009-08-01 08:00', 'arrived')
        window.add('2009-08-01 10:00', 'Operations: Programming: #123: foo')
        window.add('2009-08-01 10:15', '#123: foo')
        window.add('2009-08-02 08:00', 'arrived')
        window.add('2009-08-02 09:00', '#123: bar')
        entries = convert(window)
        self.assertEqual(2, len(entries))
        self.assertEqual(2.25, entries[0].duration)
        self.assertEqual('Operations: Programming: #123: foo, #123: foo',
                         entries[0].comment)
        self.assertEqual(1, entries[1].duration)


if __name__ == '__main__':
    unittest.main()
