#!/usr/bin/env python3
# encoding: utf-8
# @licence AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>
# @author Copyright (C) 2015 Robin Schneider <ypid@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, version 3 of the
# License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Telnet login script.
"""

__version__ = '0.5'

# modules {{{
# std {{{
import re
import logging
# }}}

from lxml import etree
# }}}


class CdCatDatabase:
    _RE_RSYNC = re.compile(
        r'(?P<file_type>[a-z-])(?P<perms>[A-Za-z-]+)'
        r'\s+(?P<size>[0-9,.]+)\s+(?P<date>[^ ]+)\s+(?P<path>.*)$'
    )

    def __init__(
        self,
        input_file,
        output_file,
        from_format='rsync',
        to_format='cdcat',
    ):

        self._input_file = input_file
        self._output_file = output_file
        self._from_format = from_format
        self._to_format = to_format

        self.convert()

    def convert(self):
        self._output_fh = open(self._output_file, 'w')

        root = etree.Element(u'root')
        root.append(etree.Comment(
            u" CD Catalog Database file, generated by {}".format(os.path.basename(__file__))
            u"Homepage: <a href=\"http://cdcat.sf.net\">http://cdcat.sf.net</a>  Author: Christoph Thielecke  (crissi99@gmx.de)"
            u"Program-Version: UNICODE 1.8, Database-Version: 2.1"
         )
        child = etree.Element('child')
        child.text = 'some text'
        root.append(child)

        # pretty string
        s = etree.tostring(root, pretty_print=True).decode('UTF-8')
        self._output_fh.write(s)
        print(s)

        {
            'rsync': self._parse_rsync(),
        }[self._from_format]

    def _parse_rsync(self):
        with open(self._input_file) as input_file:
            for line in input_file:
                re_match = self._RE_RSYNC.match(line)
                size = self._sizeof_fmt(int(re_match.group('size').replace(',', '')))
                logging.debug(
                    u"Parsed line: type: {}, perms: {}, size: {}, date: {}, path: {}".format(
                        re_match.group('file_type'),
                        re_match.group('perms'),
                        size,
                        re_match.group('date'),
                        re_match.group('path'),
                    )
                )
                break

    def _sizeof_fmt(self, num):
        for unit in ['byte', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb']:
            if abs(num) < 1024.0:
                return "{:,} {}".format(num, unit).replace('.', ',')
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yb')


def main(args):

    converter = CdCatDatabase(
        args.input_file,
        args.output,
        from_format=args.from_format,
        to_format=args.to_format,
    )

if __name__ == '__main__':
    from argparse import ArgumentParser

    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.DEBUG,
        # level=logging.INFO,
    )
    args = ArgumentParser(
        description=u"Converter for cdcat database format.",
        epilog=__doc__,
    )
    args.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__),
    )
    args.add_argument(
        'input_file',
        help=u"Input file.",
    )
    args.add_argument(
        '-f',
        '--from',
        dest='from_format',
        help=u"Specify input format."
        u" FORMAT can 'rsync' (default) for a input file generated by 'rsync --recursive --list-only'.",
        default='rsync',
    )
    args.add_argument(
        '-t',
        '--to',
        dest='to_format',
        help=u"Specify output format."
        u" FORMAT can be cdcat (default)",
        default='cdcat',
    )
    args.add_argument(
        '-o',
        '--output',
        required=True,
        help=u"Output file.",
    )
    user_parms = args.parse_args()

    main(user_parms)