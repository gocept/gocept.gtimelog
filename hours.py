import pkg_resources
pkg_resources.require('lxml')

import urllib
import urllib2
from datetime import timedelta

from lxml import etree

import gtimelog


import time

class Memoize(object):
    """Memoize With Timeout"""
    _caches = {}
    _timeouts = {}

    def __init__(self,timeout=2):
        self.timeout = timeout

    def collect(self):
        """Clear cache of results which have timed out"""
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache

    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._timeouts[f] = self.timeout

        def func(*args, **kwargs):
            kw = kwargs.items()
            kw.sort()
            key = (args, tuple(kw))
            try:
                v = self.cache[key]
                print "cache"
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                print "new"
                v = self.cache[key] = f(*args,**kwargs),time.time()
            return v[0]

        return func


class HourTracker(object):
    days = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']

    def __init__(self, settings):
        self.settings = settings

        pw_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pw_mgr.add_password(None,
                            settings.hours_url,
                            settings.hours_username,
                            settings.hours_password)
        auth_handler = urllib2.HTTPBasicAuthHandler(pw_mgr)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

    def downloadWeek(self, week, year):
        view_url = '%s?view_name=%s&view_week=%d&view_year=%d&view=1' % (
            self.settings.hours_url, self.settings.hours_username,
            week, year)
        data = self.getPage(view_url)
        return data

    def loadWeek(self, week, year):
        data = self.downloadWeek(week, year)
        tree = etree.HTML(data)

        self.tree = tree
        self.week = week
        self.year = year

        self.loadProjects()
        self.loadTasks()

    @Memoize(3000)
    def getPage(self, url):
        response = urllib2.urlopen(url)
        data = response.read()
        return data

    def loadProjects(self):
        tree = self.tree

        self.projects_full = {}
        self.projects_simple = {}
        self.projects_transformed = {}

        for option in tree.xpath('//select[@name="p1"]/option'):
            project = option.get('value')
            if project == 'Select project....':
                continue

            # exact form
            self.projects_full[project.lower()] = project

            # w/o customer-id
            self.projects_simple[project.lower().split('-')[0]] = project

            # mangled
            self.projects_transformed[self._transform_project(project)] = \
                    project

    def loadTasks(self):
        tree = self.tree
        self.tasks = tasks = {}
        for task in tree.xpath('//select[@name="t1"]/option'):
            tasks[task.text.lower().strip()] = task.get('value')
            
    def setHours(self, hour_tuples):
        self.hours = {}
        for start, stop, duration, entry in hour_tuples:
            if not duration:
                continue
            if entry.endswith('**'):
                continue
            print "%s -> %s" % (start, stop),
            project, task, desc = self.mapEntry(entry)
            if desc.endswith('/2'):
                # if task ends with /2 divide the duration by two
                duration /= 2
                desc = desc[:-2]
            print '[%s] [%s] %s %s' % (project, task, duration, desc)
            
            weekday = self.days[start.weekday()]

            self.hours.setdefault(project, {}). \
                    setdefault(task, {}). \
                    setdefault(weekday, []). \
                    append((duration, desc))

    def saveWeek(self):
        data = self._get_empty_form()
        data.update(self._aggregate_hour_data())

        data['name'] = self.settings.hours_username
        data['year'] = self.year
        data['week'] = self.week
        data['curr_week'] = self.week

        request = urllib2.Request(self.settings.hours_url,
                                  urllib.urlencode(data))
        result = urllib2.urlopen(request)
        # read the contents of result, otherwise python2.5 will not do the
        # request
        result.readlines()
    
    def _get_empty_form(self):
        form = {}
        for name in self.tree.xpath('(//select|//input)/@name'):
            form[name] = ''
        return form

    def _aggregate_hour_data(self):
        row = 0
        data = {}
        for project, tasks in self.hours.items():
            for task, days in tasks.items():
                row += 1
                data['p%d' % row] = project
                data['t%d' % row] = task
                comments = []
                for day, entries in days.items():
                    time = sum((e[0] for e in entries), timedelta(0))
                    time = time.seconds / 3600.0
                    time = round(time * 4 ) / 4  # round to .25
                    data['%s%d' % (day, row)] = time

                    day_comments = (e[1].strip() for e in entries)
                    day_comments = (c for c in day_comments if c)
                    comments.extend(day_comments)
                    

                data['opm%d' % row] = unicode('; '.join(set(comments)),
                                              'utf-8').encode('latin1')
        print '%d rows' % row
        return data

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

    def findProject(self, project):
        trans_p = self._transform_project(project)
        lower = project.lower()

        match = self.projects_full.get(lower)
        if match is None:
            match = self.projects_simple.get(lower)
        if match is None:
            match = self.projects_transformed.get(trans_p)
        if match is None:
            candidates = [p for p in self.projects_transformed
                          if p.startswith(trans_p)]

            if len(candidates) > 1:
                raise ValueError("Ambigous project %r, found %r" % (
                    project, candidates))
            if candidates:
                match = self.projects_transformed[candidates[0]]

        if match is None:
            raise KeyError("Couldn't match project %r" % project)

        return match

    def findTask(self, task):
        "Match an (abreviated) task name."
        match = self.tasks.get(task)
        if match is None:
            candidates = [t for t in self.tasks if t.startswith(task)]
            if len(candidates) > 1:
                raise ValueError("Ambigous task %r, found %r" % (
                        task, candidates))
            if candidates:
                match = self.tasks.get(candidates[0])
        if match is None:
            raise KeyError("Could not match task %r" % task)
        return match
    
    @classmethod
    def _transform_project(cls, project):
        project = project.split('-')[0]
        return project.strip().lower().replace('_', ' ')


if __name__ == '__main__':
    hour = HourTracker()
    hour.loadWeek(10, 2006)
