# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import re


def calc_duration(duration):
    """Calculates duration and returns tuple (h, m)"""
    return divmod((duration.days * 24 * 60 + duration.seconds // 60), 60)


def calc_progress(settings, timelog, week_window):
    """Calculate the progress of a given week window."""
    min, max = week_window
    weeks = (max - min).days / 7
    weekly_window = timelog.window_for(min, max)
    week_total_work, week_total_slacking, week_total_holidays = (
        weekly_window.totals())

    week_done = calc_duration(week_total_work)[0]
    week_exp = ((settings.week_hours * weeks) -
                calc_duration(week_total_holidays)[0])
    week_todo = int(week_exp) - week_done

    return week_done, week_exp, week_todo


def format_duration(duration):
    """Format a datetime.timedelta with minute precision."""
    return '%d h %d min' % calc_duration(duration)


def format_duration_short(duration):
    """Format a datetime.timedelta with minute precision."""
    return '%d:%02d' % calc_duration(duration)


def format_duration_long(duration):
    """Format a datetime.timedelta with minute precision, long format."""
    h, m = calc_duration(duration)
    if h and m:
        return '%d hour%s %d min' % (h, h != 1 and "s" or "", m)
    elif h:
        return '%d hour%s' % (h, h != 1 and "s" or "")
    else:
        return '%d min' % m


def uniq(l):
    """Return list with consecutive duplicates removed."""
    result = l[:1]
    for item in l[1:]:
        if item != result[-1]:
            result.append(item)
    return result


def different_days(dt1, dt2, virtual_midnight):
    """Check whether dt1 and dt2 are on different "virtual days".

    See virtual_day().
    """
    return virtual_day(dt1, virtual_midnight) != virtual_day(dt2,
                                                             virtual_midnight)


def parse_datetime(dt):
    """Parse a datetime instance from 'YYYY-MM-DD HH:MM' formatted string."""
    m = re.match(r'^(\d+)-(\d+)-(\d+) (\d+):(\d+)$', dt)
    if not m:
        raise ValueError('bad date time: ', dt)
    year, month, day, hour, min = map(int, m.groups())
    return datetime.datetime(year, month, day, hour, min)


def virtual_day(dt, virtual_midnight):
    """Return the "virtual day" of a timestamp.

    Timestamps between midnight and "virtual midnight" (e.g. 2 am) are
    assigned to the previous "virtual day".
    """
    if dt.time() < virtual_midnight:     # assign to previous day
        return dt.date() - datetime.timedelta(1)
    return dt.date()


def parse_time(t):
    """Parse a time instance from 'HH:MM' formatted string."""
    m = re.match(r'^(\d+):(\d+)$', t)
    if not m:
        raise ValueError('bad time: ', t)
    hour, min = map(int, m.groups())
    return datetime.time(hour, min)
