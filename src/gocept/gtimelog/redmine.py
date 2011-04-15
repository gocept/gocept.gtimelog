from pyactiveresource.activeresource import ActiveResource
from zope.cachedescriptors.property import Lazy as cachedproperty
import datetime
import logging
import re


log = logging.getLogger(__name__)


class TimelogEntry(object):

    def __init__(self, date, duration, issue, comment):
        self.date = date.strftime('%Y-%m-%d')
        self.duration = duration
        self.issue = issue
        self.project = self.parse_project(comment)
        self.comment = ''
        self.add_comment(comment)

    def parse_project(self, comment):
        parts = comment.split(':')
        # Project: Activity: Comment
        if len(parts) >= 3:
            return parts[0]

    def add_comment(self, comment):
        parts = re.split('\s*:\s*', comment)
        if len(parts) > 2:
            comment = ': '.join(parts[2:])
        if self.comment:
            self.comment += ', '
        self.comment += comment


def duration_to_float(duration):
    result = duration.seconds / 3600.0
    result = round(result * 4) / 4  # round to .25
    return result


def comment_to_issue(comment):
    match = re.search(r'#(\d+)', comment)
    if not match:
        return
    return match.group(1)


def timelog_to_issues(window):
    """converts a gtimelog window into a list of TimelogEntries.

    Multiple entries for the same issue per day are consolidated into one
    TimelogEntry.
    """

    entries = {}
    order = []
    for start, stop, duration, comment in window.all_entries():
        issue = comment_to_issue(comment)
        if not issue:
            continue
        day = datetime.date(start.year, start.month, start.day)
        duration = duration_to_float(duration)
        key = (issue, day)
        if key not in entries:
            entries[key] = TimelogEntry(day, duration, issue, comment)
            order.append(key)
        else:
            entries[key].duration += duration
            entries[key].add_comment(comment)

    # XXX I'd much rather use a StableDict here, but we can't really afford
    # dependencies until gtimelog is eggified
    result = []
    for key in order:
        result.append(entries[key])
    return result


class RedmineTimelogUpdater(object):

    def __init__(self, settings):
        self.connections = []
        for config in settings.redmines:
            redmine = RedmineConnection(
                config['url'], config['api_key'], config['activity'])
            redmine.projects = config['projects']
            self.connections.append(redmine)

    def find_connection(self, project):
        for redmine in self.connections:
            for p in redmine.projects:
                if project.lower().startswith(p.lower()):
                    return redmine
        return None

    def update(self, window):
        for entry in timelog_to_issues(window):
            redmine = self.find_connection(entry.project)
            if not redmine:
                continue

            try:
                redmine.update_entry(entry)
            except Exception, e:
                log.error(
                    'Error updating #%s (%s)' % (entry.issue, entry.date),
                    exc_info=True)
                raise RuntimeError(
                    '#%s %s: %s' % (entry.issue, entry.date, str(e)))

    def get_subject(self, issue_id, project):
        redmine = self.find_connection(project.match_string)
        return redmine and redmine.get_subject(issue_id)


class ApiKeyResource(ActiveResource):
    """Some Redmine installations have trouble with Basic Auth, so we pass the
    API key along with every request instead."""

    @classmethod
    def _query_string(cls, query_options):
        if query_options is None:
            query_options = {}
        query_options['key'] = cls._user
        return super(ApiKeyResource, cls)._query_string(query_options)


class RedmineConnection(object):

    def __init__(self, url, api_key, activity):
        self.url = url
        self.api_key = api_key
        self.activity = activity

    def api(self, type_):
        return type(type_, (ApiKeyResource,), {
            '_site': self.url,
            '_user': self.api_key,
            '_password': ''})

    @cachedproperty
    def user(self):
        return self.api('User').get('current')

    def update_entry(self, entry):
        self._delete_existing_entries(entry)
        self.api('TimeEntry').create(dict(
            hours=entry.duration,
            issue_id=entry.issue,
            spent_on=entry.date,
            comments=entry.comment,
            activity_id=self.activity))

    def get_subject(self, issue_id):
        return self.api('Issue').find(issue_id).subject

    def _delete_existing_entries(self, timelog_entry):
        entries = self.api('TimeEntry').find(issue_id=timelog_entry.issue)
        for entry in entries:
            if entry.user.id != self.user['id']:
                continue
            # Redmine returns time entries of subtasks, too, so we need to
            # filter those
            if entry.issue != timelog_entry.issue:
                continue
            if entry.spent_on != timelog_entry.date:
                continue
            entry.destroy()
