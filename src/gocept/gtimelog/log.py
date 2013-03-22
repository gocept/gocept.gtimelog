# -*- coding: utf-8 -*-
# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import argparse
import gocept.gtimelog.cli
import os.path


def log():
    """Create a new logentry"""
    # Start logging
    # Argument parsing
    parser = argparse.ArgumentParser(
        description=u'Add a new timelog entry.')
    parser.add_argument(
        'log',
        nargs='*',
        help='Your log.')
    args = parser.parse_args()

    # Load config
    settings, timelog = gocept.gtimelog.cli.load_config_and_timelog()
    timelog.append(' '.join(args.log))


def download():
    """Download projects and tasks."""

    settings, timelog = gocept.gtimelog.cli.load_config_and_timelog()
    configdir = os.path.expanduser('~/.gtimelog')
    tasks = gocept.gtimelog.collmex.TaskList(
        os.path.join(configdir, 'tasks-collmex.txt'), settings)
    tasks.reload()
