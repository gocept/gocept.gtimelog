#!/usr/bin/python2.7
# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

"""Convert hamster database entries into gtimelog format.

This utility reads records from a specified time range out of a hamster time
tracker database and outputs it as gtimelog-compatible text records.
"""

import argparse
import datetime
import sqlite3
import sys


def grind(dt):
    """Reduce datetime `dt` to minute granularity."""
    return dt.replace(second=0, microsecond=0)


class Facts(object):

    """Collection of facts from the hamster database."""

    def __init__(self, database, start, end=None):
        self.conn = sqlite3.connect(
            database, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        self.start = start
        self.end = end

    def _facts_query(self, cursor):
        """Generate fact rows."""
        conditions = 'f.start_time >= ?'
        params = [self.start]
        if self.end:
            conditions += ' AND f.start_time < ?'
            params += [self.end]
        query = """\
SELECT f.start_time, f.end_time, c.name AS category, a.name AS activity,
        f.description, f.id
FROM facts f LEFT JOIN activities a ON f.activity_id = a.id
             LEFT JOIN categories c ON a.category_id = c.id
WHERE {0}
ORDER BY f.start_time""".format(conditions)
        return cursor.execute(query, params)

    @staticmethod
    def _tags_query(cursor, fact_id):
        """Generate tag rows for fact `fact_id`."""
        query = """\
SELECT t.name
FROM tags t JOIN fact_tags ft ON t.id = ft.tag_id
WHERE ft.fact_id = ?"""
        return cursor.execute(query, (fact_id,))

    def query(self):
        """Generate Fact objects matching the date range."""
        conn = self.conn.cursor()
        for fact_row in list(self._facts_query(conn)):
            tags = list(self._tags_query(conn, fact_row['id']))
            yield Fact(fact_row, tags)

    def render(self):
        """Return gtimelog representation as multi-line string."""
        out = []
        last = None
        for fact in self.query():
            out.append(fact.render_line(last))
            last = fact
        return u''.join(out)


class Fact(object):

    """A single fact from the hamster database."""

    def __init__(self, row, tag_rows):
        self.start_time = grind(row['start_time'].replace(second=0))
        self.end_time = grind(row['end_time'] or datetime.datetime.now())
        self.category = row['category']
        self.activity = row['activity']
        desc_items = [row['description']] + [t['name'] for t in tag_rows]
        self.description = u' '.join([d for d in desc_items if d])

    def special_line(self, keyword):
        """Render start_time as first line of a day."""
        return '{0}: {1}\n'.format(
            self.start_time.strftime('%Y-%m-%d %H:%M'), keyword)

    def regular_line(self):
        """Render as regular text line containing all attributes."""
        return u'{1}: {0.category}: {0.activity}: {0.description}\n'.format(
            self, self.end_time.strftime('%Y-%m-%d %H:%M'))

    def render_line(self, lastfact=None):
        """Render depending on the last fact seen."""
        if not lastfact or self.start_time.date() != lastfact.end_time.date():
            return u'\n' + self.special_line(u'arrived') + self.regular_line()
        if lastfact.end_time == self.start_time:
            return self.regular_line()
        return self.special_line(u'pause **') + self.regular_line()


def parse_date(datestr):
    return datetime.datetime.strptime(datestr, '%Y-%m-%d')


def main():
    """Parse command line arguments and conduct conversion."""
    default_start = datetime.datetime.now().strftime('%Y-01-01')
    default_end = datetime.datetime.now().strftime('%Y-%m-%d')
    argp = argparse.ArgumentParser(
        description=__doc__,
        epilog=u'Start date and end date are meant inclusive '
               u'and must be given in %Y-%m-%d notation.')
    argp.add_argument('database', metavar=u'DATABASE',
                      help='hamster database file')
    argp.add_argument('-s', '--start', metavar=u'DATE',
                      default=default_start, type=parse_date,
                      help=u'Print records from DATE (default: %(default)s)')
    argp.add_argument('-e', '--end', metavar=u'DATE',
                      default=default_end, type=parse_date,
                      help=u'Print records until DATE (default: %(default)s)')
    args = argp.parse_args()
    facts = Facts(args.database, args.start, args.end)
    sys.stdout.write(facts.render().encode('UTF-8'))


if __name__ == '__main__':
    main()
