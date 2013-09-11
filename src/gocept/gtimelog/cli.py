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


def load_config_and_timelog():
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

    return settings, timelog


def configure_logging(debug=False):
    # Start logging
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s'))
    if debug:
        stdout.setLevel(logging.DEBUG)
    else:
        stdout.setLevel(logging.INFO)
        logging.getLogger('pyactiveresource.connection').setLevel(
            logging.WARNING)
    logging.root.addHandler(stdout)


def main():
    """Run the program."""
        # Argument parsing
    parser = argparse.ArgumentParser(
        description=u'Upload timelog data for a week to all backends '
                    u'(Redmine, Collmex, Hourtracker)')
    parser.add_argument(
        '--day',
        metavar='YYYY-MM-DD',
        default=datetime.today().strftime('%Y-%m-%d'),
        help='Day of the week that should be uploaded. '
             '(default: today)')
    parser.add_argument(
        '-d', '--debug',
        help='Enable debug logging',
        action='store')
    args = parser.parse_args()

    configure_logging(debug=args.debug)

    # Load config
    settings, timelog = load_config_and_timelog()

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
        log.info('Collmex: success')

    # 2. redmine
    try:
        redupdate = gocept.gtimelog.redmine.RedmineTimelogUpdater(
            settings)
        redupdate.update(window)
    except Exception:
        log.error('Error filling Redmine', exc_info=True)
    else:
        log.info('Redmine: success')
