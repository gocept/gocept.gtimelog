# -*- coding: utf-8 -*-
# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import print_function
from datetime import datetime, timedelta, date
from gocept.gtimelog.util import format_duration_long
import argparse
import gocept.gtimelog.cli
import gocept.gtimelog.core
import gocept.gtimelog.util
import sys

try:
    import curses
except ImportError:
    curses = None


class WithColors(object):

    RED = '\033[1m'
    BLACK = '\033[0m'


class WithoutColors(object):

    RED = ''
    BLACK = ''


HOLIDAYS = [
    date(2016, 1, 1),
    date(2016, 1, 6),
    date(2016, 3, 25),
    date(2016, 3, 28),
    date(2016, 5, 5),
    date(2016, 5, 16),
    date(2016, 10, 3),
    date(2016, 10, 31),
    date(2016, 12, 26),
]


def get_businessdays_until_now():
    """Return amount of businessdays of current month until today.

     This allows showing a progress over the current month and the
     current year.
    """

    now = datetime.now()
    businessdays = 0
    for i in range(1, now.day + 1):
        thisdate = date(now.year, now.month, i)
        if thisdate.weekday() < 5 and thisdate not in HOLIDAYS:
            businessdays += 1
    return businessdays


def main():
    global Colors
    """Run the program."""
    Colors = WithoutColors
    if curses:
        try:
            curses.setupterm()
            curses.initscr()
            if curses.can_change_color():
                Colors = WithColors
            curses.endwin()
        except curses.error:
            Colors = WithoutColors

    # Argument parsing
    parser = argparse.ArgumentParser(
        description=u'Show the progress of the current week')
    parser.add_argument(
        '--day',
        metavar='YYYY-MM-DD',
        default=datetime.today().strftime('%Y-%m-%d'),
        help='Day of the week the progress should be calculated for. '
             '(default: today)')
    args = parser.parse_args()

    # Load config
    settings, timelog = gocept.gtimelog.cli.load_config_and_timelog()

    # Calculate the progress
    today = datetime.strptime(args.day, '%Y-%m-%d')
    monday = today - timedelta(today.weekday())
    sunday = monday + timedelta(7)

    week_done, week_exp, week_todo = gocept.gtimelog.util.calc_progress(
        settings, timelog, (monday, sunday))

    today_window = timelog.window_for(today, today + timedelta(1))
    today_window.daily_report_timeline(
        sys.stdout, settings.email, settings.name)

    total_work, total_slacking, total_holidays = (
        timelog.window_for(monday, sunday).totals())

    print("Total work done this week:   {colors.RED}{total_work}{colors.BLACK}"
          " of {colors.RED}{expected} hours{colors.BLACK}".format(
              colors=Colors,
              total_work=format_duration_long(total_work),
              expected=int(week_exp)))

    first_of_month = datetime(today.year, today.month, 1)
    next_month = today.replace(day=28) + timedelta(days=4)
    last_of_month = next_month - timedelta(days=next_month.day)
    total_customer, total_intern, total_slacking, total_holidays = (
        timelog.window_for(first_of_month, last_of_month).totals(True))
    total_work = total_customer + total_intern

    if total_work.total_seconds():
        total_percent = (total_customer.total_seconds() * 100.0 /
                         total_work.total_seconds())
    else:
        total_percent = 0
    expected = progress_expected = 0
    engagement = settings.engagement
    if engagement:
        expected = engagement[today.month - 1]
        progress_expected = int(get_businessdays_until_now() * settings.hours)

    print("Total work done this month: {colors.RED}{total_work} "
          "({total_percent} %){colors.BLACK} of {colors.RED}{progress_expected}"
          " ({expected}) hours{colors.BLACK}".format(
              colors=Colors,
              progress_expected=progress_expected,
              expected=expected,
              total_work=format_duration_long(total_work),
              total_percent=round(total_percent, 1)))

    first_of_year = datetime(today.year, 1, 1)
    last_of_year = datetime(today.year, 12, 31)
    total_customer, total_intern, total_slacking, total_holidays = (
        timelog.window_for(first_of_year, last_of_year).totals(True))
    total_work = total_customer + total_intern

    total_percent = (total_customer.total_seconds() * 100.0 /
                     total_work.total_seconds())
    progress_engagement = 0
    now = datetime.now()
    for i in range(1, now.month + 1):
        if i < now.month:
            progress_engagement += settings.engagement[i - 1]
        else:
            progress_engagement += int(
              get_businessdays_until_now() * settings.hours)
    engagement = sum(settings.engagement)

    print("Total work done this year:  {colors.RED}{total_work} "
          "({total_percent} %){colors.BLACK} of {colors.RED}{progress} "
          "({expected}) hours{colors.BLACK}".format(
              colors=Colors,
              progress=progress_engagement,
              expected=engagement,
              total_work=format_duration_long(total_work),
              total_percent=round(total_percent, 1)))

    if not today_window.items:
        return
    d_hours = timedelta(hours=today_window.settings.week_hours / 5.0)
    time_left = d_hours - today_window.totals()[0]
    clock_off = today_window.items[0][0] + d_hours + today_window.totals()[1]
    print("")
    print("Time left at work:           {colors.RED}{time_left}{colors.BLACK}"
          " (until {until})".format(
              colors=Colors,
              time_left=format_duration_long(time_left),
              until=clock_off.strftime('%H:%M')))
