# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.gtimelog.util import different_days, format_duration_long
import ConfigParser
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
            f = open(self.filename)
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
                entry = unicode(entry.strip(), 'utf-8')
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
        work = work.values()
        work.sort()
        slack = slack.values()
        slack.sort()
        hold = hold.values()
        hold.sort()
        return work, slack, hold

    def totals(self):
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
        """
        total_work = total_slacking = total_holiday = datetime.timedelta(0)
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
                total_work += duration
        return total_work, total_slacking, total_holiday

    def icalendar(self, output):
        """Create an iCalendar file with activities."""
        print >> output, "BEGIN:VCALENDAR"
        print >> output, "PRODID:-//mg.pov.lt/NONSGML GTimeLog//EN"
        print >> output, "VERSION:2.0"
        try:
            import socket
            idhost = socket.getfqdn()
        except:  # can it actually ever fail?
            idhost = 'localhost'
        dtstamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        for start, stop, duration, entry in self.all_entries():
            print >> output, "BEGIN:VEVENT"
            print >> output, "UID:%s@%s" % (hash((start, stop, entry)), idhost)
            print >> output, "SUMMARY:%s" % (entry.replace('\\', '\\\\')
                                                  .replace(';', '\\;')
                                                  .replace(',', '\\,'))
            print >> output, "DTSTART:%s" % start.strftime('%Y%m%dT%H%M%S')
            print >> output, "DTEND:%s" % stop.strftime('%Y%m%dT%H%M%S')
            print >> output, "DTSTAMP:%s" % dtstamp
            print >> output, "END:VEVENT"
        print >> output, "END:VCALENDAR"

    def daily_report(self, output, email, who):
        """Format a daily report.

        Writes a daily report template in RFC-822 format to output.
        """
        # Locale is set as a side effect of 'import gtk', so strftime('%a')
        # would give us translated names
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekday = weekday_names[self.min_timestamp.weekday()]
        week = self.min_timestamp.strftime('%V')
        print >> output, "To: %(email)s" % {'email': email}
        print >> output, ("Subject: %(date)s report for %(who)s"
                          " (%(weekday)s, week %(week)s)"
                          % {'date': self.min_timestamp.strftime('%Y-%m-%d'),
                             'weekday': weekday, 'week': week, 'who': who})
        print >> output
        items = list(self.all_entries())
        if not items:
            print >> output, "No work done today."
            return
        start, stop, duration, entry = items[0]
        entry = entry[:1].upper() + entry[1:]
        print >> output, "%s at %s" % (entry, start.strftime('%H:%M'))
        print >> output
        work, slack, hold = self.grouped_entries()
        total_work, total_slacking, total_holidays = self.totals()
        if work:
            for start, entry, duration in work:
                entry = entry[:1].upper() + entry[1:]
                print >> output, "%-62s  %s" % (entry,
                                                format_duration_long(duration))
            print >> output
        print >> output, ("Total work done: %s" %
                          format_duration_long(total_work))
        print >> output
        if slack:
            for start, entry, duration in slack:
                entry = entry[:1].upper() + entry[1:]
                print >> output, "%-62s  %s" % (entry,
                                                format_duration_long(duration))
            print >> output
        print >> output, ("Time spent slacking: %s" %
                          format_duration_long(total_slacking))

    def daily_report_timeline(self, output, email, who):
        """Format a daily report with your timeline entries."""
        # Locale is set as a side effect of 'import gtk', so strftime('%a')
        # would give us translated names
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekday = weekday_names[self.min_timestamp.weekday()]
        week = self.min_timestamp.strftime('%V')
        print >> output, ("%(date)s report for %(who)s"
                          " (%(weekday)s, week %(week)s)"
                          % {'date': self.min_timestamp.strftime('%Y-%m-%d'),
                             'weekday': weekday, 'week': week, 'who': who})
        print >> output
        items = list(self.all_entries())
        if not items:
            print >> output, "No work done today."
            return
        start, stop, duration, entry = items[0]
        for start, stop, duration, entry in items[1:]:
            print >> output, "%s - %s (%3s): %s" % (
                start.strftime('%H:%M'), stop.strftime('%H:%M'),
                duration.seconds / 60, entry.encode('utf-8'))
        now = datetime.datetime.now()
        if stop.date() == now.date():
            print >> output, "%s - %s (%3d): **current task**" % (
                stop.strftime('%H:%M'), now.strftime('%H:%M'),
                (now - stop).seconds / 60)
        print >> output
        work, slack, hold = self.grouped_entries()
        total_work, total_slacking, total_holidays = self.totals()
        print >> output, ("Total work done today:     %s" %
                          format_duration_long(total_work))

    def weekly_report(self, output, email, who, estimated_column=False):
        """Format a weekly report.

        Writes a weekly report template in RFC-822 format to output.
        """
        week = self.min_timestamp.strftime('%V')
        print >> output, "To: %(email)s" % {'email': email}
        print >> output, "Subject: Weekly report for %s (week %s)" % (who,
                                                                      week)
        print >> output
        items = list(self.all_entries())
        if not items:
            print >> output, "No work done this week."
            return
        print >> output, " " * 46,
        if estimated_column:
            print >> output, "estimated       actual"
        else:
            print >> output, "                time"
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
                    print >> output, ("%-46s  %-14s  %s" %
                                (entry, '-', format_duration_long(duration)))
                else:
                    print >> output, ("%-62s  %s" %
                                (entry, format_duration_long(duration)))
            print >> output
        print >> output, ("Total work done this week: %s" %
                          format_duration_long(total_work))


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
        f = open(self.filename, "a")
        if self.need_space:
            self.need_space = False
            print >> f
        print >> f, line
        f.close()

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
        f = open(self.filename, 'r')
        lines = f.readlines()
        f.close()
        f = open(self.filename, 'w')
        f.writelines(lines[:-1])
        f.close()
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
            for line in file(self.filename):
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
        self.groups = groups.items()
        self.groups.sort()

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

    enable_gtk_completion = True  # False enables gvim-style completion

    hours = 8
    week_hours = 40
    virtual_midnight = datetime.time(2, 0)

    task_list_url = ''
    project_list_url = ''
    edit_task_list_cmd = ''

    log_level = 'ERROR'

    collmex_customer_id = ''
    collmex_company_id = 1
    collmex_employee_id = ''
    collmex_username = ''
    collmex_password = ''
    collmex_task_language = 'en'

    hours_url = 'http://cosmos.infrae.com/uren/'
    hours_username = ''
    hours_password = ''

    redmines = []

    def _config(self):
        config = ConfigParser.RawConfigParser()
        config.add_section('gtimelog')
        config.set('gtimelog', 'list-email', self.email)
        config.set('gtimelog', 'name', self.name)
        config.set('gtimelog', 'editor', self.editor)
        config.set('gtimelog', 'mailer', self.mailer)
        config.set('gtimelog', 'gtk-completion',
                   str(self.enable_gtk_completion))
        config.set('gtimelog', 'hours', str(self.hours))
        config.set('gtimelog', 'week_hours', str(self.week_hours))
        config.set('gtimelog', 'virtual_midnight',
                   self.virtual_midnight.strftime('%H:%M'))
        config.set('gtimelog', 'edit_task_list_cmd', self.edit_task_list_cmd)
        config.set('gtimelog', 'log_level', self.log_level)

        config.add_section('collmex')
        config.set('collmex', 'customer_id', self.collmex_customer_id)
        config.set('collmex', 'company_id', self.collmex_company_id)
        config.set('collmex', 'employee_id', self.collmex_employee_id)
        config.set('collmex', 'username', self.collmex_username)
        config.set('collmex', 'password', self.collmex_password)
        config.set('collmex', 'task_language', self.collmex_task_language)

        config.add_section('hours')
        config.set('hours', 'url', self.hours_url)
        config.set('hours', 'username', self.hours_username)
        config.set('hours', 'password', self.hours_password)
        config.set('hours', 'tasks', self.task_list_url)
        config.set('hours', 'projects', self.project_list_url)

        return config

    def load(self, filename):
        config = self._config()
        config.read([filename])
        self.email = config.get('gtimelog', 'list-email')
        self.name = config.get('gtimelog', 'name')
        self.editor = config.get('gtimelog', 'editor')
        self.mailer = config.get('gtimelog', 'mailer')
        self.enable_gtk_completion = config.getboolean('gtimelog',
                                                       'gtk-completion')
        self.hours = config.getfloat('gtimelog', 'hours')
        self.week_hours = config.getfloat('gtimelog', 'week_hours')
        self.virtual_midnight = gocept.gtimelog.util.parse_time(
            config.get('gtimelog', 'virtual_midnight'))
        self.edit_task_list_cmd = config.get('gtimelog', 'edit_task_list_cmd')

        self.log_level = getattr(logging, config.get('gtimelog', 'log_level'))

        self.collmex_customer_id = config.get('collmex', 'customer_id')
        self.collmex_company_id = config.get('collmex', 'company_id')
        self.collmex_employee_id = config.get('collmex', 'employee_id')
        self.collmex_username = config.get('collmex', 'username')
        self.collmex_password = config.get('collmex', 'password')
        self.collmex_task_language = config.get('collmex', 'task_language')

        self.hours_url = config.get('hours', 'url')
        self.hours_username = config.get('hours', 'username')
        self.hours_password = config.get('hours', 'password')
        self.task_list_url = config.get('hours', 'tasks')
        self.project_list_url = config.get('hours', 'projects')

        for section in config.sections():
            if not section.startswith('redmine'):
                continue
            redmine = dict(config.items(section))
            if redmine['url'].endswith('/'):
                redmine['url'] = redmine['url'][:-1]
            redmine['projects'] = redmine['projects'].split()
            self.redmines.append(redmine)

    def save(self, filename):
        config = self._config()
        f = file(filename, 'w')
        try:
            config.write(f)
        finally:
            f.close()
