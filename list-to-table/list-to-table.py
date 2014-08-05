#!/usr/bin/env python
# encoding: utf-8
# @author Robin Schneider <ypid23@aol.de>
# @licence GPLv3 <http://www.gnu.org/licenses/gpl.html>

__version__ = '0.9'

# modules {{{
import os
import codecs
import logging
import re

import csv
# }}}

# module wide variables {{{
SCRIPT_URL = 'https://github.com/ypid/scripts/blob/master/list-to-table/list-to-table.py'
# }}}

class ListToTable:
    def __init__(
            self,
            raw_filepath,
            csv_filepath,
            wanted_properties=(),
            default_properties=('Model', 'Price'),
            find_model_and_price=re.compile(ur'\A(?P<model>.+) ab €(?P<price>\d+),(?:--|\d{2})')
    ):

        self.__find_model_and_price = find_model_and_price

        self._raw_file_fh = codecs.open(raw_filepath,  'r', 'UTF-8')
        self._csv_file_fh = codecs.open(csv_filepath,  'wb', 'UTF-8')
        self._csv = csv.writer(self._csv_file_fh, delimiter=';')
        self._wanted_properties = default_properties + wanted_properties

        self._csv.writerow(self._wanted_properties)

        self._parse_raw_file()

    def _parse_raw_file(self):
        """
        Parse raw file.
        """

        for line in self._raw_file_fh:
            if re.match(r'\s*$', line):
                continue

            model_and_price_match = self.__find_model_and_price.search(line)
            if model_and_price_match is None:
                logging.warn('Could not find model and price in line: %s', line)
                continue

            model = model_and_price_match.group('model')
            price = model_and_price_match.group('price')
            logging.info('Item model: %s, price: %s', model, price)

            line = line[model_and_price_match.end():]

            wanted_properties = []
            properties = self._parse_properties(line)
            properties['Model'] = model
            properties['Price'] = price
            for wanted_key in self._wanted_properties:
                if wanted_key in properties:
                    wanted_properties.append(properties[wanted_key])

            self._csv.writerow(wanted_properties)

    def _parse_properties(self, string):
        """
        Return dict for property string line: Diagonale: 50"/127cm • Auflösung: 1920x1080 • Panel: Plasma
        """

        properties = dict()
        for match in re.finditer(ur'(?P<key>\w+): (?P<value>[^•]+)(?: •)?', string):
            key = match.group('key')
            value = match.group('value').rstrip()
            properties[key] = value

        return properties


def main():  # {{{
    """Execute module in command line mode."""

    args = ArgumentParser(
        description="Uses the database from cdcat to copy wanted files.",
        epilog="Implementation of the work flow explained here:"
        + " http://superuser.com/a/717689",
    )
    args.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    args.add_argument(
        '-v',
        '--verbosity',
        action='count',
        default=0,
        help="Be more verbose."
    )
    args.add_argument(
        'file',
        help="raw test file file",
    )
    args.add_argument(
        '-w',
        '--wanted',
        help="Wanted property fields."
    )
    user_parms = args.parse_args()
    wanted_properties = ()
    if user_parms.wanted:
        wanted_properties = tuple(user_parms.wanted.split(','))

    logging.basicConfig(
        format='# %(levelname)s: %(message)s',
        # level=logging.DEBUG,
        level=logging.INFO,
    )
    logging.info(u"Running cdcat-parser: %s", SCRIPT_URL)

    l2t_parser = ListToTable(
        user_parms.file,
        user_parms.file + '.csv',
        wanted_properties=wanted_properties
    )

if __name__ == '__main__':
    from argparse import ArgumentError, ArgumentParser
    import sys

    main()
# }}}
