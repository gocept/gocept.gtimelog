# -*- coding: utf-8 -*-
# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime, timedelta
import argparse
import gocept.gtimelog.core
import gocept.gtimelog.util
import gocept.gtimelog.cli
import sys


def main():
    """Run the program."""

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

    seperator = '#'.join(['' for x in range(80)])

    print "\nTotal work done in week %s: \033[1m%s\033[0mh of "\
          "\033[1m%s\033[0mh" % (today.strftime("%W"),
                                 float(week_done),
                                 week_exp)
    print "\n%s\n" % seperator

    today_window = timelog.window_for(today, today + timedelta(1))
    today_window.daily_report(sys.stdout, settings.email, settings.name)
    print "\n%s\n" % seperator

    week_window = timelog.window_for(monday, sunday)
    week_window.weekly_report(sys.stdout, settings.email, settings.name)
