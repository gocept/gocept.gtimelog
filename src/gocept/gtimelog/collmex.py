# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.collmex.collmex

class Collmex(object):

    def __init__(self, settings):
        self.settings = settings
        self.collmex = gocept.collmex.collmex.Collmex(
            self.settings.collmex_customer_id,
            self.settings.collmex_company_id,
            self.settings.collmex_username,
            self.settings.collmex_password)
        self.projects = self.getProjectsAndTasks()

    def report(self, entries):
        pass

    def getProjectsAndTasks(self):
        projects = {}
        for result in self.collmex.get_projects():
            if result['Abgeschlossen'] != u'0':
                continue
            pid = result['Projektnummer']
            project = projects.get(pid)
            if project is None:
                projects[pid] = project = MatchableObject(
                    result['Bezeichnung'], pid, [])
            project.references.append(MatchableObject(
                result['Satz Bezeichnung'], result['Satz Nr']))
        return [p for p in projects.values()]

    def mapEntry(self, entry):
        parts = entry.split(':')

        if len(parts) < 2:
            raise ValueError("Couldn't split %r correctly" % entry)

        project = parts[0].strip()
        task = parts[1].strip().lower()
        desc = ':'.join(parts[2:]).strip()

        project = self.findProject(project)
        actual_task = self.findTask(task)

        return project, actual_task, desc


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
        raise ValueError("Ambigous matchable %r, found %r" % (
            match_string, [c.match_string for c in candidates]))
    if candidates:
        return candidates[0]
    raise ValueError("Couldn't match %r" % match_string)
