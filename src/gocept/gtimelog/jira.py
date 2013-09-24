from __future__ import absolute_import
import jira.client


class Jira(object):

    def __init__(self, url, username, password, projects):
        self.url = url
        self.username = username
        self.projects = projects
        self.api = jira.client.JIRA(
            options={'server': url}, basic_auth=(username, password))

    def update_entry(self, entry):
        issue = self.api.issue(entry.issue)
        self._delete_existing_entries(entry, issue)
        worklog = self.api.add_worklog(issue, timeSpent='%sh' % entry.duration)
        # unfortunately, Jira does not allow setting ``created`` or ``updated``
        worklog.update(comment='%s: %s' % (entry.date, entry.comment))

    def get_subject(self, issue_id):
        return self.api.issue(issue_id).fields.summary

    def _delete_existing_entries(self, timelog_entry, issue):
        for entry in self.api.worklogs(issue):
            if entry.author.name != self.username:
                continue
            if not getattr(entry, 'comment', '').startswith(
                    timelog_entry.date):
                continue
            entry.delete()


# XXX workaround for <https://bitbucket.org/bspeakmon/jira-python/issue/60>

def set_options(self, value):
    self._real_options = {}
    self._real_options.update(value)


def get_options(self):
    return self._real_options

jira.client.JIRA._options = property(get_options, set_options)
