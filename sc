#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: 2017-2020 Robin Schneider <ypid@riseup.net>
# SPDX-License-Identifier: AGPL-3.0-only

"""
systemctl wrapper.

Features:

* Switch command and name. Example: sc nginx restart
* Allow multiple commands. Example: sc nginx stop disable mask
* Proper RFC 3339 date format. The format for the additional weekday was taken from systemd.time(7).

Ref: https://github.com/systemd/systemd/issues/14515
"""

from __future__ import (print_function, unicode_literals,
                        absolute_import, division)

import sys
import os
import re
import logging
import pydoc

from argparse import ArgumentParser, RawTextHelpFormatter

# No hard depend on third party modules which might not be installed.
try:
    import pexpect
except ImportError:
    pass

__version__ = '0.4.1'
__maintainer__ = 'Robin Schneider <ypid@riseup.net>'
LOG = logging.getLogger(__name__)


def single_execute(name, command):
    call = ['systemctl']

    if name is not None:
        if '.' not in name:
            name += '.service'
        call.extend([command if (command is not None) else 'status', name])

    LOG.info("Executing: {}".format(call))

    if 'pexpect' not in sys.modules or command not in ['status']:
        # Note, os.execvp does not flush open file objects and descriptors!
        #  os.execvp(call[0], call)
        return os.system(' '.join(call))
    else:
        environ = os.environ.copy()
        environ.update({
            'SYSTEMD_PAGER': '',
        })

        # journalctl somehow detects pexpect.runu and truncates lines.
        # Mitigation (only needed for pexpect and pty):
        call.insert(1, '--full')

        try:
            stdout, exitcode = pexpect.runu(call[0], call[1:], withexitstatus=1, env=environ)
        except TypeError:
            stdout, exitcode = pexpect.runu(' '.join(call), withexitstatus=1, env=environ)

        # Not quite working.
        # import pty
        # stdout_parts = []
        # def read(fd):
        #     data = os.read(fd, 1024)
        #     stdout_parts.append(data.decode())
        #     return data
        # exitcode = pty.spawn(call, read)
        # stdout = ''.join(stdout_parts)
        # print(stdout)
        # sys.exit(0)

        # systemctl does not output ANSI color which we want when called with subprocess.
        # import subprocess
        # process = subprocess.Popen("env", shell=False, stdout=subprocess.PIPE)
        # stdout = process.communicate()[0].decode()
        # exitcode = process.returncode

        # Refer to ./timezone-names-to-utc-offsets for an attempt to generate
        # this map.
        tz_to_offset_map = {
            'UTC': 'z',
            'CET': '+01:00',
            'CEST': '+02:00',
        }

        stdout_lines_modified = []

        re_done = False
        for line in stdout.split('\n'):

            if not re_done:
                # Active: active (running) since Sat 2020-01-25 19:06:55 CET; 1h 21min ago
                # Condition: start condition failed at Sat 2020-01-25 19:06:55 CET; 1h 20min ago
                _re = re.search(r'^(?P<pre>.* (?:since|at) .*:\d{2})(?P<tz> \w+)(?P<post>.*)(?:$|;)', line)
                if _re:
                    line = ''.join([
                        _re.group('pre'),
                        tz_to_offset_map.get(_re.group('tz').strip().upper(), _re.group('tz')),
                        _re.group('post'),
                    ])
                    re_done = True

            stdout_lines_modified.append(line)

        if len(stdout_lines_modified) > 42:
            pydoc.pager('\n'.join(stdout_lines_modified))
        else:
            print('\n'.join(stdout_lines_modified), end='')

        return exitcode


def main():
    args_parser = ArgumentParser(
        epilog=__doc__,
        formatter_class=RawTextHelpFormatter,
    )
    args_parser.add_argument('name', nargs='?', type=str)
    args_parser.add_argument('command', nargs='*', type=str, default=[None])
    args_parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__),
    )
    args_parser.add_argument(
        '-v', '--verbose', action='append_const',
        help="Verbose output.",
        dest="loglevel",
        const=1,
    )
    cli_args = args_parser.parse_args()
    if cli_args.loglevel:
        logging.basicConfig(
            format='{levelname} {message}',
            style='{',
            level=logging.INFO,
        )

    worst_exitcode = 0
    for command in cli_args.command:
        exitcode = single_execute(cli_args.name, command)
        if exitcode != 0:
            worst_exitcode = exitcode

    sys.exit(worst_exitcode)


if __name__ == '__main__':
    main()
