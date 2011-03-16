import cookielib
import datetime
import logging
import lxml.html.soupparser
import lxml.objectify
import re
import urllib
import urllib2


log = logging.getLogger(__name__)


class TimelogEntry(object):

    def __init__(self, date, duration, issue, comment):
        self.date = date
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
                config['url'], config['username'], config['password'],
                config['activity'])
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
            except urllib2.HTTPError, e:
                log.error(
                    'Error updating #%s (%s)' % (entry.issue, entry.date),
                    exc_info=True)
                raise RuntimeError(
                    '#%s %s: %s' % (entry.issue, entry.date, str(e)))

    def get_subject(self, issue_id, project):
        redmine = self.find_connection(project.match_string)
        return redmine and redmine.get_subject(issue_id, project)


class RedmineConnection(object):

    def __init__(self, url, username, password, activity):
        self.url = url
        self.username = username
        self.password = password
        self.activity = activity

        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cj))
        self.token = None
        self.activity_id = {}

    def update_entry(self, entry):
        self.login()
        self.populate_activity_ids(entry)

        # we do two things with one request here: delete existing entries and
        # retrieve the link we need to create the new entry. This is ugly from
        # the code perspective (too high coupling), but good from a performance
        # perspective (as few HTTP requests as possible)
        body = self.open('/issues/%s/time_entries?%s' % (
            entry.issue, urllib.urlencode({
                'from': entry.date, 'to': entry.date})))
        html = lxml.html.soupparser.fromstring(body)

        self.delete_existing_entries(html)

        params = {
            'authenticity_token': self.token,
            'time_entry[hours]': entry.duration,
            'time_entry[issue_id]': entry.issue,
            'time_entry[spent_on]': entry.date,
            'time_entry[comments]': entry.comment,
            'time_entry[activity_id]': self.activity_id[self.activity]
        }
        project_url = html.xpath(
            '//*[@id="main-menu"]//a[@class="overview"]')[0].get('href')
        project_url = '/'.join(project_url.split('/')[-2:])
        self.open('/%s/timelog/edit' % project_url, **params)

    def delete_existing_entries(self, html):
        row = None
        for row in html.xpath(
            '//td[@class="user" and text() = "%s"]/..' % self.full_name):
            delete_url = row.xpath('//a[contains(@href, "/destroy")]')
            if not len(delete_url):
                raise urllib2.HTTPError(
                    None, '403', 'No permission to delete time entry',
                    None, None)
            delete_url = delete_url[0].get('href')
            id = delete_url.split('/')[-2]
            self.open(
                '/time_entries/%s/destroy' % id, authenticity_token=self.token)

    def populate_activity_ids(self, entry):
        # unfortunately, the "create time entry" form is only available on an
        # issue, not globally
        if self.activity_id:
            return
        body = self.open('/issues/%s/time_entries/new' % entry.issue)
        html = lxml.html.soupparser.fromstring(body)
        for option in html.xpath(
            '//select[@id="time_entry_activity_id"]/option[@value != ""]'):
            self.activity_id[option.text] = option.get('value')

    def get_subject(self, issue_id, project):
        self.login()
        body = self.open('/issues/%s' % issue_id)
        html = lxml.html.soupparser.fromstring(body)
        subject = html.xpath('//*[@class="subject"]//h3')
        return unicode(subject[0].text)

    def login(self):
        if self.token:
            return
        body = self.open('/login')
        html = lxml.html.soupparser.fromstring(body)
        login_token = html.xpath(
            '//input[@name="authenticity_token"]')[0].get('value')
        self.open('/login',
                  authenticity_token=login_token,
                  password=self.password,
                  username=self.username)
        body = self.open('/my/account')
        html = lxml.html.soupparser.fromstring(body)
        self.token = html.xpath(
            '//input[@name="authenticity_token"]')[0].get('value')

        # we need the full name to parse the time entries table
        firstname = html.xpath('//input[@id="user_firstname"]')[0].get('value')
        lastname = html.xpath('//input[@id="user_lastname"]')[0].get('value')
        self.full_name = '%s %s' % (firstname, lastname)

    def open(self, path, **params):
        if not params:
            params = None
        else:
            params = urllib.urlencode(params)
        response = self.opener.open(self.url + path, params)
        body = response.read()
        # XXX kludgy error handling
        if 'Invalid user or password' in body:
            raise urllib2.HTTPError(
                None, '403', 'Invalid user or password', None, None)
        return body
