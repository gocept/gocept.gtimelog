from __future__ import unicode_literals
import datetime
import gocept.gtimelog.bugtracker
import gocept.gtimelog.core
import logging
import transaction


log = logging.getLogger(__name__)


# https://github.com/tick/tick-api
# https://github.com/MartinAramayo/pyTick


class Tickspot(object):

    def __init__(self, settings):
        self.tickspot_api_token = settings.tickspot_api_token
        self.tickspot_email = settings.tickspot_email
        self.tickspot_subscription_id = settings.tickspot_subscription_id
        self.projects = self.get_projects_and_tasks()

    def auth_headers(self):
        user_agent = {"User-Agent": f"Gtimelog User <{self.tickspot_email}>"}
        get_heads = {
            "Authorization": f"Token token={self.tickspot_api_token}",
            **user_agent
        }

    def report(self, entries):
        for start, stop, duration, entry in entries:
            if not duration:
                continue
            if entry.endswith('**'):
                continue
            if entry.endswith('$$$'):  # we don't track holidays
                continue
            if start > stop:
                raise ValueError("End before begin in %s (%s to %s)" % (
                                 entry, start, stop))
            task_id, desc = self.mapEntry(entry)

            break_ = datetime.timedelta(0)
            if desc.endswith('/2'):
                # if task ends with /2 divide the duration by two
                desc = desc[:-2]
                break_ = duration / 2
            log.debug("%s -> %s, [%s] [%s] %s %s" % (
                start, stop, project, task, duration, desc))

            save_tick_activity(tick_task_id, duration, desc)

    def get_projects_and_tasks(self):
        # XXX fetch from tickspot
        url = 'https://www.tickspot.com/{self.tickspot_subscription_id}/api/v2/projects.json'
        return {'project1': {'task1': '56431', 'task2': '123456'}}

    def save_tick_activity(self, tick_task_id, duration, desc):
        # XXX avoid duplicate entries
        # XXX post to tickspot

        url = ''
        data = {
            "date": datetime.today().strftime('%Y-%m-%d'),
            "hours": duration,
            "notes": desc,
            "task_id": tick_task_id,
            "user_id": os.getenv('userID')
        }

        if date:
            data.update({"date": date})

        if notes:
            data.update({"notes": notes})

        url = 'https://www.tickspot.com/{self.tickspot_subscription_id}/api/v2/entries.json'

    def mapEntry(self, entry):
        parts = entry.split(':')

        if len(parts) < 2:
            raise ValueError("Couldn't split %r correctly" % entry)

        try:
            project = match(parts[0].strip(), self.projects.keys())
            task_name = match(parts[1].strip(), self.projects[project].keys())
            task_id = self.projects[project][task_name]
        except ValueError, e:
            message = e.args[0]
            raise ValueError("While mapping '%s': %s" % (entry, message))
        desc = ':'.join(parts[2:]).strip()

        return task_id, desc


class MatchableObject(object):
    """This can be either a project or a task."""

    def __init__(self, match_string, id, references=None):
        self.references = references
        self.id = id

        self.match_string = match_string
        self.match_simple = self.transform_simple(match_string)
        self.match_transformed = self.transform_matchable(match_string)

    @staticmethod
    def transform_simple(match_string):
        return match_string.lower().split('-')[0]

    @staticmethod
    def transform_matchable(match_string):
        match_transformed = match_string.split('-')[0]
        return match_transformed.strip().lower().replace('_', ' ')

    def __str__(self):
        return self.match_string


def match(match_string, matchables):
    lower_m = match_string.lower()
    simple_m = MatchableObject.transform_simple(match_string)
    trans_m = MatchableObject.transform_matchable(match_string)
    for matchable in matchables:
        if lower_m == matchable.match_string.lower():
            return matchable
    for matchable in matchables:
        if simple_m == matchable.match_simple.lower():
            return matchable
    candidates = [m for m in matchables
                  if m.match_transformed.startswith(trans_m)]

    if len(candidates) > 1:
        raise ValueError("Ambigous matchable '%s', found '%s'" % (
            match_string, [c.match_string for c in candidates]))
    if candidates:
        return candidates[0]
    raise ValueError("Couldn't match '%s'" % match_string)


class TaskList(gocept.gtimelog.core.TaskList):

    def __init__(self, filename, settings):
        self.tickspot = Tickspot(settings)
        super(TaskList, self).__init__(filename)

    def download(self):
        projects_and_tasks = self.tickspot.get_projects_and_tasks()
        tasks = open(self.filename, 'w')
        for proj_name in projects_and_tasks.keys():
            for task_name in projects_and_tasks[proj_name].keys():
                tasks.write((
                    u'%s: %s\n' % (proj_name,
                                   task_name)).encode('utf-8'))
        tasks.close()

    def reload(self):
        self.download()
        self.load()
