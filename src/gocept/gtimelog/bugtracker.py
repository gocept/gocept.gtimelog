import collections
import datetime
import gocept.gtimelog.jira
import gocept.gtimelog.redmine
import logging
import re


log = logging.getLogger(__name__)


# The following value was determined by experimentation with gocept's redmine
# instance on May 5, 2011.
COMMENT_MAX_LENGTH = 255


class TimelogEntry(object):

    def __init__(self, date, duration, issue, comment):
        self.date = date.strftime('%Y-%m-%d')
        self.duration = duration
        self.issue = issue
        self.project = self.parse_project(comment)
        self.comments = []
        self.comment = ''
        self.add_comment(comment)

    def parse_project(self, comment):
        parts = comment.split(':')
        # Project: Activity: Comment
        if len(parts) >= 3:
            return parts[0]

    def add_comment(self, comment):
        if comment.count(':') >= 2:
            comment = comment.split(':', 2)[-1]
        comment = comment.strip()
        if comment and comment not in self.comments:
            self.comments.append(comment)
            self.comment = ', '.join(self.comments)[:COMMENT_MAX_LENGTH]


# ITracker - API that each concrete bugtracker must provide:
# projects: list of project names this tracker is applicable for
# def update_entry(entry)
# def get_subject(issue_id)


class Bugtrackers(object):

    def __init__(self, settings):
        self.trackers = []
        for config in settings.redmines:
            redmine = gocept.gtimelog.redmine.Redmine(
                config['url'], config['api_key'], config['activity'],
                config['projects'])
            self.trackers.append(redmine)
        for config in settings.jiras:
            jira = gocept.gtimelog.jira.Jira(
                config['url'], config['username'], config['password'],
                config['projects'])
            self.trackers.append(jira)

    def find_tracker(self, project):
        match_len, found = 0, None
        for tracker in self.trackers:
            for p in tracker.projects:
                if project.lower().startswith(p.lower()):
                    match_len, found = max(
                        (match_len, found), (len(p), tracker))
        return found

    @staticmethod
    def extract_issue(comment):
        match = re.search(r'#([-A-Z0-9]+)', comment)
        if not match:
            return
        return match.group(1)

    @staticmethod
    def duration_to_float(duration):
        result = duration.seconds / 3600.0
        result = round(result * 4) / 4  # round to .25
        return result

    def update(self, window):
        for entry in self._timelog_to_issues(window):
            tracker = self.find_tracker(entry.project)
            if not tracker:
                continue

            try:
                tracker.update_entry(entry)
            except Exception, e:
                log.error(
                    'Error updating #%s (%s)' % (entry.issue, entry.date),
                    exc_info=True)
                raise RuntimeError(
                    '#%s %s: %s' % (entry.issue, entry.date, str(e)))

    def get_subject(self, issue_id, project):
        tracker = self.find_tracker(project.match_string)
        return tracker and tracker.get_subject(issue_id)

    def _timelog_to_issues(self, window):
        """converts a gtimelog window into a list of TimelogEntries.

        Multiple entries for the same issue per day are consolidated into one
        TimelogEntry.
        """

        entries = collections.OrderedDict()
        for start, stop, duration, comment in window.all_entries():
            issue = self.extract_issue(comment)
            if not issue:
                continue
            day = datetime.date(start.year, start.month, start.day)
            duration = self.duration_to_float(duration)
            key = (issue, day)
            if key not in entries:
                entries[key] = TimelogEntry(day, duration, issue, comment)
            else:
                entries[key].duration += duration
                entries[key].add_comment(comment)
        return entries.values()
