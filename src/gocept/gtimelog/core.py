# Copyright (c) 2012-2013 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.gtimelog.util import different_days
from gocept.gtimelog.util import format_duration_long
from gocept.gtimelog.util import parse_date
import base64
import codecs
import configparser
import datetime
import gocept.gtimelog.util
import logging
import os


class TimeWindow(object):
    """A window into a time log.

    Reads a time log file and remembers all events that took place between
    min_timestamp and max_timestamp.  Includes events that took place at
    min_timestamp, but excludes events that took place at max_timestamp.

    self.items is a list of (timestamp, event_title) tuples.

    Time intervals between events within the time window form entries that have
    a start time, a stop time, and a duration.  Entry title is the title of the
    event that occurred at the stop time.

    The first event also creates a special "arrival" entry of zero duration.

    Entries that span virtual midnight boundaries are also converted to
    "arrival" entries at their end point.
    """

    def __init__(self, filename, min_timestamp, max_timestamp,
                 virtual_midnight, callback=None, settings=None):
        self.filename = filename
        self.min_timestamp = min_timestamp
        self.max_timestamp = max_timestamp
        self.virtual_midnight = virtual_midnight
        self.settings = settings
        self.reread(callback)

    def reread(self, callback=None):
        """Parse the time log file and update self.items."""
        self.items = []
        try:
            f = open(self.filename, encoding='utf-8')
        except IOError:
            return
        line = ''
        for line in f:
            if ': ' not in line:
                continue
            time, entry = line.split(': ', 1)
            try:
                time = gocept.gtimelog.util.parse_datetime(time)
            except ValueError:
                continue
            else:
                entry = entry.strip()
                if callback:
                    callback(entry)
                if self.min_timestamp <= time < self.max_timestamp:
                    self.items.append((time, entry))
        f.close()

    def last_time(self):
        """Return the time of the last event (or None if there are no events).
        """
        if not self.items:
            return None
        return self.items[-1][0]

    def all_entries(self):
        """Iterate over all entries.

        Yields (start, stop, duration, entry) tuples.  The first entry
        has a duration of 0.
        """
        stop = None
        for item in self.items:
            start = stop
            stop = item[0]
            entry = item[1]
            if start is None or different_days(start, stop,
                                               self.virtual_midnight):
                start = stop
            duration = stop - start
            yield start, stop, duration, entry

    def count_days(self):
        """Count days that have entries."""
        count = 0
        last = None
        for start, stop, duration, entry in self.all_entries():
            if last is None or different_days(last, start,
                                              self.virtual_midnight):
                last = start
                count += 1
        return count

    def last_entry(self):
        """Return the last entry (or None if there are no events).

        It is always true that

            self.last_entry() == list(self.all_entries())[-1]

        """
        if not self.items:
            return None
        stop = self.items[-1][0]
        entry = self.items[-1][1]
        if len(self.items) == 1:
            start = stop
        else:
            start = self.items[-2][0]
        if different_days(start, stop, self.virtual_midnight):
            start = stop
        duration = stop - start
        return start, stop, duration, entry

    def grouped_entries(self, skip_first=True):
        """Return consolidated entries (grouped by entry title).

        Returns two list: work entries, slacking entries and holidays.
        Slacking entries are identified by finding two asterisks in the
        title.
        The holidays are indicated by '$$$'.
        For entries ending with '/2' half is counted as work and other half is
        counted as slacking.
        Entry lists are sorted, and contain (start, entry, duration)
        tuples.
        """
        work = {}
        slack = {}
        hold = {}
        for start, stop, duration, entry in self.all_entries():
            if skip_first:
                skip_first = False
                continue
            if '**' in entry:
                entries_list = (slack, )
            if entry.endswith('$$$'):
                entries_list = (hold, )
            else:
                entries_list = (work, )
            if entry.endswith('/2'):
                # if entry endswith /2 count only half of the duration
                duration /= 2
                entries_list = (work, slack)
            # strip task description away
            entry = ':'.join(entry.split(':')[:2])
            for entries in entries_list:
                if entry in entries:
                    old_start, old_entry, old_duration = entries[entry]
                    start = min(start, old_start)
                    duration += old_duration
                entries[entry] = (start, entry, duration)
        work = sorted(work.values())
        slack = sorted(slack.values())
        hold = sorted(hold.values())
        return work, slack, hold

    def totals(self, split_intern_customer=False):
        """Calculate total time of work and slacking entries.

        Returns (total_work, total_slacking, total_holiday) tuple.

        Slacking entries are identified by finding two asterisks in the
        title. Holidays are identified by three $ symbols by the end of
        the entry.

        For entries ending with '/2' is half of the time is counted as work
        and the other half is counted as slacking.

        Assuming that

            total_work, total_slacking = self.totals()
            work, slacking, holidays = self.grouped_entries()

        It is always true that

            total_work = sum([duration for start, entry, duration in work])
            total_slacking = sum([duration
                                  for start, entry, duration in slacking])

        (that is, it would be true if sum could operate on timedeltas).

        If `split_intern_customer` is set to True, instead of total_work return
        total_customer and total_intern, which means work on customer projects
        and work on interal projects.
        """
        total_work = total_slacking = total_holiday = datetime.timedelta(0)
        total_customer = total_intern = datetime.timedelta(0)
        for start, stop, duration, entry in self.all_entries():
            if entry.endswith('/2'):
                duration /= 2
                total_slacking += duration
                total_work += duration
                continue
            if entry.endswith('$$$') and self.settings:
                total_holiday += duration
                continue
            if '**' in entry:
                total_slacking += duration
            else:
                if not split_intern_customer:
                    total_work += duration
                elif entry[0:2] in ['op', 'I_', 'kr']:
                    total_intern += duration
                else:
                    total_customer += duration
        if not split_intern_customer:
            return total_work, total_slacking, total_holiday
        return total_customer, total_intern, total_slacking, total_holiday

    def icalendar(self, output):
        """Create an iCalendar file with activities."""
        print("BEGIN:VCALENDAR", file=output)
        print("PRODID:-//mg.pov.lt/NONSGML GTimeLog//EN", file=output)
        print("VERSION:2.0", file=output)
        try:
            import socket
            idhost = socket.getfqdn()
        except Exception:  # can it actually ever fail?
            idhost = 'localhost'
        dtstamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        for start, stop, duration, entry in self.all_entries():
            print("BEGIN:VEVENT", file=output)
            print("UID:%s@%s" % (hash((start, stop, entry)), idhost),
                  file=output)
            print("SUMMARY:%s" % (entry.replace('\\', '\\\\')
                                  .replace(';', '\\;')
                                  .replace(',', '\\,')), file=output)
            print("DTSTART:%s" % start.strftime('%Y%m%dT%H%M%S'), file=output)
            print("DTEND:%s" % stop.strftime('%Y%m%dT%H%M%S'), file=output)
            print("DTSTAMP:%s" % dtstamp, file=output)
            print("END:VEVENT", file=output)
        print("END:VCALENDAR", file=output)

    def daily_report(self, output, email, who):
        """Format a daily report.

        Writes a daily report template in RFC-822 format to output.
        """
        # Locale is set as a side effect of 'import gtk', so strftime('%a')
        # would give us translated names
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekday = weekday_names[self.min_timestamp.weekday()]
        week = self.min_timestamp.strftime('%V')
        print("To: %(email)s" % {'email': email}, file=output)
        print(("Subject: %(date)s report for %(who)s"
               " (%(weekday)s, week %(week)s)"
               % {'date': self.min_timestamp.strftime('%Y-%m-%d'),
                  'weekday': weekday, 'week': week, 'who': who}), file=output)
        print(file=output)
        items = list(self.all_entries())
        if not items:
            print("No work done today.", file=output)
            return
        start, stop, duration, entry = items[0]
        entry = entry[:1].upper() + entry[1:]
        print("%s at %s" % (entry, start.strftime('%H:%M')), file=output)
        print(file=output)
        work, slack, hold = self.grouped_entries()
        total_work, total_slacking, total_holidays = self.totals()
        if work:
            for start, entry, duration in work:
                entry = entry[:1].upper() + entry[1:]
                print("%-62s  %s" % (entry,
                                     format_duration_long(duration)),
                      file=output)
            print(file=output)
        print(("Total work done: %s" %
               format_duration_long(total_work)), file=output)
        print(file=output)
        if slack:
            for start, entry, duration in slack:
                entry = entry[:1].upper() + entry[1:]
                print("%-62s  %s" % (entry,
                                     format_duration_long(duration)),
                      file=output)
            print(file=output)
        print(("Time spent slacking: %s" %
               format_duration_long(total_slacking)), file=output)

    def daily_report_timeline(self, output, email, who):
        """Format a daily report with your timeline entries."""
        # Locale is set as a side effect of 'import gtk', so strftime('%a')
        # would give us translated names
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekday = weekday_names[self.min_timestamp.weekday()]
        week = self.min_timestamp.strftime('%V')
        print(("%(date)s report for %(who)s"
               " (%(weekday)s, week %(week)s)"
               % {'date': self.min_timestamp.strftime('%Y-%m-%d'),
                  'weekday': weekday, 'week': week, 'who': who}), file=output)
        print(file=output)
        items = list(self.all_entries())
        if not items:
            print("No work done today.", file=output)
            return
        start, stop, duration, entry = items[0]
        for start, stop, duration, entry in items[1:]:
            print("%s - %s (%3s): %s" % (
                start.strftime('%H:%M'), stop.strftime('%H:%M'),
                duration.seconds // 60, entry), file=output)
        now = datetime.datetime.now()
        if stop.date() == now.date():
            print("%s - %s (%3d): **current task**" % (
                stop.strftime('%H:%M'), now.strftime('%H:%M'),
                (now - stop).seconds / 60), file=output)
        print(file=output)
        work, slack, hold = self.grouped_entries()
        total_work, total_slacking, total_holidays = self.totals()
        print(("Total work done today:       %s" %
               format_duration_long(total_work)), file=output)

    def weekly_report(self, output, email, who, estimated_column=False):
        """Format a weekly report.

        Writes a weekly report template in RFC-822 format to output.
        """
        week = self.min_timestamp.strftime('%V')
        print("To: %(email)s" % {'email': email}, file=output)
        print("Subject: Weekly report for %s (week %s)" % (who,
                                                           week), file=output)
        print(file=output)
        items = list(self.all_entries())
        if not items:
            print("No work done this week.", file=output)
            return
        print(" " * 46, end=' ', file=output)
        if estimated_column:
            print("estimated       actual", file=output)
        else:
            print("                time", file=output)
        work, slack, hold = self.grouped_entries()
        total_work, total_slacking, total_holidays = self.totals()
        if work:
            work = [(entry, duration) for start, entry, duration in work]
            work.sort()
            for entry, duration in work:
                if not duration:
                    continue  # skip empty "arrival" entries
                entry = entry[:1].upper() + entry[1:]
                if estimated_column:
                    print(("%-46s  %-14s  %s" %
                           (entry, '-',
                            format_duration_long(duration))), file=output)
                else:
                    print(("%-62s  %s" %
                           (entry, format_duration_long(duration))),
                          file=output)
            print(file=output)
        print(("Total work done this week: %s" %
               format_duration_long(total_work)), file=output)


class TimeLog(object):
    """Time log.

    A time log contains a time window for today, and can add new entries at
    the end.
    """

    def __init__(self, filename, settings):
        self.filename = filename
        self.settings = settings
        self.virtual_midnight = settings.virtual_midnight
        self.reread()

    def reread(self):
        """Reload today's log."""
        self.day = gocept.gtimelog.util.virtual_day(
            datetime.datetime.now(), self.virtual_midnight)
        min = datetime.datetime.combine(self.day, self.virtual_midnight)
        max = min + datetime.timedelta(1)
        self.history = []
        self.window = TimeWindow(self.filename, min, max,
                                 self.virtual_midnight,
                                 callback=self.history.append,
                                 settings=self.settings)
        self.need_space = not self.window.items

    def window_for(self, min, max):
        """Return a TimeWindow for a specified time interval."""
        return TimeWindow(self.filename, min, max,
                          self.virtual_midnight,
                          settings=self.settings)

    def raw_append(self, line):
        """Append a line to the time log file."""
        with open(self.filename, "a") as f:
            if self.need_space:
                self.need_space = False
                print(file=f)
            print(line, file=f)

    def append(self, entry):
        """Append a new entry to the time log."""
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        last = self.window.last_time()
        if last and different_days(now, last, self.virtual_midnight):
            # next day: reset self.window
            self.reread()
        self._append(now, entry)

    def _append(self, time, text):
        self.window.items.append((time, text))
        line = '%s: %s' % (time.strftime("%Y-%m-%d %H:%M"), text)
        self.raw_append(line)

    def weekly_window(self, day=None):
        if not day:
            day = self.day
        monday = day - datetime.timedelta(day.weekday())
        min = datetime.datetime.combine(monday, self.virtual_midnight)
        max = min + datetime.timedelta(7)
        return self.window_for(min, max)

    def pop(self):
        last = self.window.items[-1]
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        with open(self.filename, 'w') as f:
            f.writelines(lines[:-1])
        self.reread()
        return last


class TaskList(object):
    """Task list.

    You can have a list of common tasks in a text file that looks like this

        Arrived **
        Reading mail
        Project1: do some task
        Project2: do some other task
        Project1: do yet another task

    These tasks are grouped by their common prefix (separated with ':').
    Tasks without a ':' are grouped under "Other".

    A TaskList has an attribute 'groups' which is a list of tuples
    (group_name, list_of_group_items).
    """

    other_title = 'Other'

    loading_callback = None
    loaded_callback = None
    error_callback = None

    def __init__(self, filename):
        self.filename = filename
        self.load()

    def check_reload(self):
        """Look at the mtime of tasks.txt, and reload it if necessary.

        Returns True if the file was reloaded.
        """
        mtime = self.get_mtime()
        if mtime != self.last_mtime:
            self.load()
            return True
        else:
            return False

    def get_mtime(self):
        """Return the mtime of self.filename, or None if the file doesn't
        exist."""
        try:
            return os.stat(self.filename).st_mtime
        except OSError:
            return None

    def load(self):
        """Load task list from a file named self.filename."""
        groups = {}
        self.last_mtime = self.get_mtime()
        try:
            with open(self.filename, encoding='utf-8') as lines:
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if ':' in line:
                        group, task = [s.strip() for s in line.split(':', 1)]
                    else:
                        group, task = self.other_title, line
                    groups.setdefault(group, []).append(task)
        except IOError:
            pass  # the file's not there, so what?
        self.groups = sorted(groups.items())

    def reload(self):
        """Reload the task list."""
        self.load()


class Settings(object):
    """Configurable settings for GTimeLog."""

    # Insane defaults
    email = 'activity-list@example.com'
    name = 'Anonymous'

    editor = 'gvim'
    mailer = 'x-terminal-emulator -e mutt -H %s'

    engagement = []

    # the holidays for the current year. used for gtl-progress
    holidays = []

    hours = 8
    week_hours = 40
    virtual_midnight = datetime.time(2, 0)

    edit_task_list_cmd = ''

    log_level = 'ERROR'
    decode_passwords = ''

    collmex_customer_id = ''
    collmex_company_id = 1
    collmex_employee_id = ''
    collmex_username = ''
    collmex_password = ''
    collmex_task_language = 'en'
    collmex_task_file = 'tasks.txt'

    redmines = []
    disabled_trackers = []

    def _config(self):
        config = configparser.RawConfigParser()
        config.add_section('gtimelog')
        config.set('gtimelog', 'list-email', self.email)
        config.set('gtimelog', 'name', self.name)
        config.set('gtimelog', 'editor', self.editor)
        config.set('gtimelog', 'mailer', self.mailer)
        config.set('gtimelog', 'engagement', self.engagement)
        config.set('gtimelog', 'holidays', self.holidays)
        config.set('gtimelog', 'hours', str(self.hours))
        config.set('gtimelog', 'week_hours', str(self.week_hours))
        config.set('gtimelog', 'virtual_midnight',
                   self.virtual_midnight.strftime('%H:%M'))
        config.set('gtimelog', 'edit_task_list_cmd', self.edit_task_list_cmd)
        config.set('gtimelog', 'log_level', self.log_level)
        config.set('gtimelog', 'decode_passwords', self.decode_passwords)

        config.add_section('collmex')
        config.set('collmex', 'customer_id', self.collmex_customer_id)
        config.set('collmex', 'company_id', self.collmex_company_id)
        config.set('collmex', 'employee_id', self.collmex_employee_id)
        config.set('collmex', 'username', self.collmex_username)
        config.set('collmex', 'password', self.collmex_password)
        config.set('collmex', 'task_language', self.collmex_task_language)
        config.set('collmex', 'task_file', self.collmex_task_file)

        return config

    def load(self, filename):
        config = self._config()
        config.read([filename])
        self.email = config.get('gtimelog', 'list-email')
        self.name = config.get('gtimelog', 'name')
        self.editor = config.get('gtimelog', 'editor')
        self.mailer = config.get('gtimelog', 'mailer')
        self.engagement = config.get('gtimelog', 'engagement')
        if self.engagement:
            self.engagement = [int(e) for e in self.engagement.split(',')]
        self.holidays = config.get('gtimelog', 'holidays')
        if self.holidays:
            self.holidays = [parse_date(e) for e in self.holidays.split()]
        self.hours = config.getfloat('gtimelog', 'hours')
        self.week_hours = config.getfloat('gtimelog', 'week_hours')
        self.virtual_midnight = gocept.gtimelog.util.parse_time(
            config.get('gtimelog', 'virtual_midnight'))
        self.edit_task_list_cmd = config.get('gtimelog', 'edit_task_list_cmd')

        self.log_level = getattr(logging, config.get('gtimelog', 'log_level'))
        self.decode_passwords = config.get('gtimelog', 'decode_passwords')

        def decode_password(password):
            if self.decode_passwords == 'base64':
                return base64.b64decode(password)
            elif self.decode_passwords == 'rot13':
                return codecs.decode(password, codec='rot13')
            elif not self.decode_passwords:
                return password
            raise ValueError(
                'Unknown password encoding %r.' % self.decode_passwords)

        self.collmex_customer_id = config.get('collmex', 'customer_id')
        self.collmex_company_id = config.get('collmex', 'company_id')
        self.collmex_employee_id = config.get('collmex', 'employee_id')
        self.collmex_username = config.get('collmex', 'username')
        self.collmex_password = decode_password(config.get(
            'collmex', 'password'))
        self.collmex_task_language = config.get('collmex', 'task_language')
        self.collmex_task_file = config.get('collmex', 'task_file')

        for section in config.sections():
            if section.startswith('redmine'):
                redmine = dict(config.items(section))
                if redmine['url'].endswith('/'):
                    redmine['url'] = redmine['url'][:-1]
                redmine['projects'] = redmine['projects'].split()
                self.redmines.append(redmine)
            if section.startswith('disabled'):
                disabled = dict(config.items(section))
                disabled['projects'] = disabled['projects'].split()
                self.disabled_trackers.append(disabled)

    def save(self, filename):
        config = self._config()
        with open(filename, 'w', encoding='utf-8') as f:
            config.write(f)
