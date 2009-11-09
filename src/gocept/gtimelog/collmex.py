# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.collmex.collmex
import gocept.collmex.model
import gocept.gtimelog.redmine
import logging
import transaction

log = logging.getLogger(__name__)

def get_collmex(settings):
    return gocept.collmex.collmex.Collmex(
        settings.collmex_customer_id,
        settings.collmex_company_id,
        settings.collmex_username,
        settings.collmex_password)


class Collmex(object):

    def __init__(self, settings):
        self.settings = settings
        self.collmex = get_collmex(self.settings)
        self.projects = self.getProjectsAndTasks()

    def report(self, entries):
        # Collmex needs the entries sorted by project, date and employee
        redmine_subjects = {}
        entries = sorted(entries, key=lambda x:(x[3], x[0]))

        for start, stop, duration, entry in entries:
            if not duration:
                continue
            if entry.endswith('**'):
                continue
            if entry.endswith('$$$'): # we don't track holidays
                continue
            project, task, desc = self.mapEntry(entry)

            break_ = datetime.timedelta(0)
            if desc.endswith('/2'):
                # if task ends with /2 divide the duration by two
                desc = desc[:-2]
                break_ = duration / 2
            log.debug("%s -> %s, [%s] [%s] %s %s" % (
                start, stop, project, task, duration, desc))

            assert start.date() == stop.date()

            # Get subject from redmine
            red = gocept.gtimelog.redmine.RedmineTimelogUpdater(self.settings)
            issue = gocept.gtimelog.redmine.comment_to_issue(entry)
            if issue:
                subject = redmine_subjects.get(issue)
                if not subject:
                    subject = red.get_subject(issue, project)
                    redmine_subjects[issue] = subject
                if subject:
                    desc = '%s (%s)' % (subject, desc)

            act = gocept.collmex.model.Activity()
            act['Projekt Nr'] = project.id
            act['Mitarbeiter Nr'] = self.settings.collmex_employee_id
            act['Satz Nr'] = task.id
            act['Beschreibung'] = desc
            act['Datum'] = start.date()
            act['Von'] = start.time()
            act['Bis'] = stop.time()
            act['Pausen'] = break_
            self.collmex.create(act)

        try:
            transaction.commit()
        except gocept.collmex.collmex.APIError:
            transaction.abort()
            raise

    def getProjectsAndTasks(self):
        products = dict(
            (p['Produktnummer'], p) for p in self.collmex.get_products())
        projects = {}
        for result in self.collmex.get_projects():
            if result['Abgeschlossen'] != u'0':
                continue
            pid = result['Projektnummer']
            project = projects.get(pid)
            if project is None:
                projects[pid] = project = MatchableObject(
                    result['Bezeichnung'], pid, [])
            project.references.append(
                MatchableObject(result['Satz Bezeichnung'], result['Satz Nr']))
            product = products.get(result['Produktnummer'])
            if product and product['Bezeichnung Eng']:
                project.references.append(
                    MatchableObject(product['Bezeichnung Eng'],
                                    result['Satz Nr']))
        return [p for p in projects.values()]

    def mapEntry(self, entry):
        parts = entry.split(':')

        if len(parts) < 2:
            raise ValueError("Couldn't split %r correctly" % entry)

        project = match(parts[0].strip(), self.projects)
        task = match(parts[1].strip(), project.references)
        desc = ':'.join(parts[2:]).strip()

        return project, task, desc


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
        raise ValueError("Ambigous matchable %r, found %r" % (
            match_string, [c.match_string for c in candidates]))
    if candidates:
        return candidates[0]
    raise ValueError("Couldn't match %r" % match_string)
