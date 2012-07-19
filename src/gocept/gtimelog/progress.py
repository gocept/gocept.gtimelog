# -*- coding: utf-8 -*-
# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime, timedelta
import argparse
import gocept.gtimelog.core
import gocept.gtimelog.util
import logging
import os.path
import sys


log = logging.getLogger(__name__)


def main():
    """Run the program."""
    # Start logging
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s'))
    logging.root.addHandler(stdout)

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
    configdir = os.path.expanduser('~/.gtimelog')
    try:
        os.makedirs(configdir)  # create it if it doesn't exist
    except OSError:
        pass
    settings = gocept.gtimelog.core.Settings()
    settings_file = os.path.join(configdir, 'gtimelogrc')
    if not os.path.exists(settings_file):
        settings.save(settings_file)
    else:
        settings.load(settings_file)
    logging.root.setLevel(settings.log_level)
    log.debug('Logging is set to level %s' % settings.log_level)

    # Initialize data structures
    timelog = gocept.gtimelog.core.TimeLog(
        os.path.join(configdir, 'timelog.txt'), settings)

    # Calculate the progress
    today = datetime.strptime(args.day, '%Y-%m-%d')
    monday = today - timedelta(today.weekday())
    sunday = monday + timedelta(7)

    week_done, week_exp, week_todo = gocept.gtimelog.util.calc_progress(
        settings, timelog, (monday, sunday))

    print "%s (%s)" % (float(week_done), week_exp)
