import datetime
import re
import urllib
import urllib2


class TimelogEntry(object):

    def __init__(self, date, duration, issue, comment=None):
        self.date = date
        self.duration = duration
        self.issue = issue
        self.comment = comment

        self.project = None
        parts = self.comment.split(':')
        try:
            first = parts[0]
            if '#' not in first:
                self.project = first
        except IndexError:
            pass


def duration_to_float(duration):
    result = duration.seconds / 3600.0
    result = round(result * 4 ) / 4  # round to .25
    return result


def timelog_to_issues(window):
    """converts a gtimelog window into a list of TimelogEntries.

    Multiple entries for the same issue per day are consolidated into one
    TimelogEntry.
    """

    entries = {}
    order = []
    for start, stop, duration, comment in window.all_entries():
        match = re.search(r'#(\d+)', comment)
        if not match:
            continue
        day = datetime.date(start.year, start.month, start.day)
        issue = match.group(1)
        duration = duration_to_float(duration)
        key = (issue, day)
        if key not in entries:
            entries[key] = TimelogEntry(day, duration, issue, comment)
            order.append(key)
        else:
            entries[key].duration += duration
            entries[key].comment += ', %s' % comment

    # XXX I'd much rather use a StableDict here, but we can't really afford
    # dependencies until gtimelog is eggified
    result = []
    for key in order:
        result.append(entries[key])
    return result


class RedmineTimelogUpdater(object):

    def __init__(self, settings):
        self.settings = settings
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

    def update(self, window):
        if not self.settings.redmine_url:
            return
        self.login()
        for entry in timelog_to_issues(window):
            if not self._entry_wanted(entry):
                continue

            try:
                self.update_entry(entry)
            except urllib2.HTTPError, e:
                raise RuntimeError(
                    '#%s %s: %s' % (entry.issue, entry.date, str(e)))

    def _entry_wanted(self, entry):
        update = False
        for project in self.settings.redmine_projects:
            if entry.project.startswith(project):
                return True
        return False

    def update_entry(self, entry):
        params = urllib.urlencode(dict(
            issue_id=entry.issue,
            spent_on=entry.date,
            hours=entry.duration
            ))
        self.open('/timelog/update_entry', params)

    def login(self):
        params = urllib.urlencode(dict(
            username=self.settings.redmine_username,
            password=self.settings.redmine_password))
        self.open('/login', params)

    def open(self, path, params):
        response = self.opener.open(self.settings.redmine_url + path, params)
        # XXX kludgy error handling
        if 'Invalid user or password' in response.read():
            raise RuntimeError('Invalid user or password')
