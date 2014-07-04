# Copyright (c) 2012-2013 gocept gmbh & co. kg
# See also LICENSE.txt

import argparse
import datetime
import gocept.gtimelog.collmex
import gocept.gtimelog.core
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
                    u'(Redmine, Collmex)')
    parser.add_argument(
        '--day',
        metavar='YYYY-MM-DD',
        default=None,
        help='Day of the week that should be uploaded. '
             '(default: last 7 days, including today)')
    parser.add_argument(
        '-d', '--debug',
        help='Enable debug logging',
        action='store_const',
        const=True)
    args = parser.parse_args()

    configure_logging(debug=args.debug)

    # Load config
    settings, timelog = load_config_and_timelog()

    if args.day:
        day = datetime.datetime.strptime(args.day, '%Y-%m-%d').date()
        window = timelog.weekly_window(day=day)
    else:
        begin = datetime.datetime.combine(
            datetime.date.today() - datetime.timedelta(days=7),
            timelog.virtual_midnight)
        end = datetime.datetime.combine(
            datetime.date.today() + datetime.timedelta(days=1),
            timelog.virtual_midnight)
        window = timelog.window_for(begin, end)
    log.info('Uploading %s to %s', window.min_timestamp, window.max_timestamp)

    # 1. collmex
    try:
        collmex = gocept.gtimelog.collmex.Collmex(settings)
        collmex.report(window.all_entries())
    except Exception:
        log.error('Error filling collmex', exc_info=True)
    else:
        log.info('Collmex: success')

    # 2. Bugtracker
    try:
        redupdate = gocept.gtimelog.bugtracker.Bugtrackers(
            settings)
        redupdate.update(window)
    except Exception:
        log.error('Error filling Bugtracker', exc_info=True)
    else:
        log.info('Bugtracker: success')
