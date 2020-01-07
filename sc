#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
systemctl wrapper.

Features:

* Switch command and name. Example: sc nginx restart
* Proper ISO 8601 date format.

Ref: https://github.com/systemd/systemd/issues/14515
"""

__version__ = '0.3.0'
__license__ = 'AGPL-3.0-only'
__author__ = 'Robin Schneider <ypid@riseup.net>'
__copyright__ = [
    'Copyright (C) 2020 Robin Schneider <ypid@riseup.net>',
]

import sys
import os
import re
import pydoc

import pexpect


if __name__ == '__main__':
    args = dict(zip(['name', 'command'], sys.argv[1:]))

    if 'name' in args:
        args.setdefault('command', 'status')

        if '.' not in args['name']:
            args['name'] += '.service'
    else:
        args.setdefault('command', 'list-units')

    call = ['systemctl', args['command']]
    if 'name' in args:
        call.append(args['name'])

    if args['command'] not in ['status']:
        # Note, os.execvp does not flush open file objects and descriptors!
        os.execvp(call[0], call[1:])
        #  os.system(call)
    else:
        environ = os.environ.copy()
        environ.update({
            'SYSTEMD_PAGER': '',
        })

        # journalctl somehow detects pexpect.runu and truncates lines.
        # Midigation (only needed for pexpect and pty):
        call.insert(1, '--full')

        try:
            stdout, exitstatus = pexpect.runu(call[0], call[1:], withexitstatus=1, env=environ)
        except TypeError:
            stdout, exitstatus = pexpect.runu(' '.join(call), withexitstatus=1, env=environ)

        # Not quite working.
        # import pty
        # stdout_parts = []
        # def read(fd):
        #     data = os.read(fd, 1024)
        #     stdout_parts.append(data.decode())
        #     return data
        # exitstatus = pty.spawn(call, read)
        # stdout = ''.join(stdout_parts)
        # print(stdout)
        # sys.exit(0)

        # systemctl does not output ANSI color which we want when called with subprocess.
        # import subprocess
        # process = subprocess.Popen("env", shell=False, stdout=subprocess.PIPE)
        # stdout = process.communicate()[0].decode()
        # exitstatus = process.returncode

        tz_to_offset_map = {
            'UTC': 'z',
            'CET': '+01:00',
            'CEST': '+02:00',
        }

        stdout_lines_modified = []

        re_done = False
        for line in stdout.split('\n'):

            if not re_done:
                _re = re.search(r'^(?P<pre>\s*Active:.*:\d{2})(?P<tz> \w+)(?P<post>.*)$', line)
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

        sys.exit(exitstatus)
