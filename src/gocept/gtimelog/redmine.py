from pyactiveresource.activeresource import ActiveResource
from zope.cachedescriptors.property import Lazy as cachedproperty


class ApiKeyResource(ActiveResource):
    """Some Redmine installations have trouble with Basic Auth, so we pass the
    API key along with every request instead."""

    @classmethod
    def _query_string(cls, query_options):
        if query_options is None:
            query_options = {}
        query_options['key'] = cls._user
        return super(ApiKeyResource, cls)._query_string(query_options)


class Redmine(object):

    def __init__(self, url, api_key, activity, projects):
        self.url = url
        self.api_key = api_key
        self.activity = activity
        self.projects = projects

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
