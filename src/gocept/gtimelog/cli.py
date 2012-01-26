# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime
import argparse
import gocept.gtimelog.collmex
import gocept.gtimelog.core
import gocept.gtimelog.hours
import gocept.gtimelog.redmine
import logging
import os
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
        description=u'Upload timelog data for a week to all backends '
            '(Redmine, Collmex, Hourtracker)')
    parser.add_argument(
        'day',
        metavar='YYYY-MM-DD',
        help='A day of the week that should be uploaded.')
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

    # upload to all backends

    day = datetime.strptime(args.day, '%Y-%m-%d').date()
    log.info('Uploading for week of %s' % day)
    window = timelog.weekly_window(day=day)
    # 1. collmex
    try:
        collmex = gocept.gtimelog.collmex.Collmex(settings)
        collmex.report(window.all_entries())
    except Exception:
        log.error('Error filling collmex', exc_info=True)
    else:
        log.info('Collmex: succes')

    # 2. hourtracker
    tracker = gocept.gtimelog.hours.HourTracker(settings)
    week = int(window.min_timestamp.strftime('%V'))
    year = int(window.min_timestamp.strftime('%Y'))
    try:
        tracker.loadWeek(week, year)
        tracker.setHours(window.all_entries())
        tracker.saveWeek()
    except Exception:
        log.error('Error filling HT', exc_info=True)
    else:
        log.info('Hourtracker: success')

    # 3. redmine
    try:
        redupdate = gocept.gtimelog.redmine.RedmineTimelogUpdater(
            settings)
        redupdate.update(window)
    except Exception:
        log.error('Error filling Redmine', exc_info=True)
    else:
        log.info('Redmine: success')
