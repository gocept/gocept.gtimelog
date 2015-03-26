# -*- coding: utf-8 -*-
# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import print_function
from datetime import datetime, timedelta
from gocept.gtimelog.util import format_duration_long
import argparse
import curses
import gocept.gtimelog.cli
import gocept.gtimelog.core
import gocept.gtimelog.util
import sys


class Colors(object):

    RED = '\033[1m'
    BLACK = '\033[0m'


class NoColors(object):

    RED = ''
    BLACK = ''


def main():
    global Colors
    """Run the program."""

    try:
        curses.setupterm()
    except curses.error:
        Colors = NoColors
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

    total_percent = (total_customer.total_seconds() * 100.0 /
                     total_work.total_seconds())
    expected = 0
    engagement = settings.engagement
    if engagement:
        expected = engagement[today.month - 1]

    print("Total work done this month: {colors.RED}{total_work} "
          "({total_percent} %){colors.BLACK} of  {colors.RED}{expected} "
          "hours{colors.BLACK}".format(
              colors=Colors,
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
    engagement = sum(settings.engagement)

    print("Total work done this year:  {colors.RED}{total_work} "
          "({total_percent} %){colors.BLACK} of {colors.RED}{expected} "
          "hours{colors.BLACK}".format(
              colors=Colors,
              expected=engagement,
              total_work=format_duration_long(total_work),
              total_percent=round(total_percent, 1)))


    d_hours = timedelta(hours=today_window.settings.week_hours / 5.0)
    time_left = d_hours - today_window.totals()[0]
    clock_off = today_window.items[0][0] + d_hours + today_window.totals()[1]
    print("")
    print("Time left at work:           {colors.RED}{time_left}{colors.BLACK}"
          " (until {until})".format(
              colors=Colors,
              time_left=format_duration_long(time_left),
              until=clock_off.strftime('%H:%M')))
