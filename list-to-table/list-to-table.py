#!/usr/bin/env python
# encoding: utf-8
# @author Robin Schneider <ypid23@aol.de>
# @licence GPLv3 <http://www.gnu.org/licenses/gpl.html>
"""
This script was written to parse a text, filter out interesting keywords and
output it as csv. It is written for one custom format which http://geizhals.de
and http://www.heise.de/preisvergleich use in the feature list of products.
"""

__version__ = '0.9'

# modules {{{
import codecs
import logging
import re
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
            default_properties=(u'Model', u'Price'),
            delimiter=u';',
            find_model_and_price=re.compile(ur'\A(?P<model>.+) ab €(?P<price>\d+),(?:--|\d{2})', re.UNICODE)
    ):

        self.__find_model_and_price = find_model_and_price

        self._raw_file_fh = codecs.open(raw_filepath,  'r', 'UTF-8')
        self._csv_file_fh = codecs.open(csv_filepath,  'wb', 'UTF-8')
        self._csv_delimiter = delimiter
        self._wanted_properties = default_properties + wanted_properties

        self._all_properties = set()

        self.__write_csv_row(self._wanted_properties)

        self._parse_raw_file()

    def __write_csv_row(self, items):
        self._csv_file_fh.write(self._csv_delimiter.join(items) + '\n')

    def _parse_raw_file(self):
        for line in self._raw_file_fh:
            if re.match(r'\s*$', line):
                continue

            model_and_price_match = self.__find_model_and_price.search(line)
            if model_and_price_match is None:
                logging.warn(u"Could not find model and price in line: %s", line)
                continue

            model = model_and_price_match.group(u'model')
            price = model_and_price_match.group(u'price')
            logging.info(u"Item model: %s, price: %s", model, price)

            line = line[model_and_price_match.end():]

            wanted_properties = []
            properties = self._parse_properties(line)
            properties[u'Model'] = model
            properties[u'Price'] = price
            self._add_to_all_properties(properties)
            for wanted_key in self._wanted_properties:
                if wanted_key in properties:
                    wanted_properties.append(properties[wanted_key])
                else:
                    wanted_properties.append('')

            self.__write_csv_row(wanted_properties)

    def _parse_properties(self, string):
        """
        Return dict for property string line:
            Diagonale: 50"/127cm • Auflösung: 1920x1080 • Panel: Plasma
        """

        properties = dict()
        for match in re.finditer(ur'(?P<key>[\w ]+): (?P<value>[^•]+)(?: •)?', string, re.UNICODE):
            key = match.group('key').lstrip()
            value = match.group('value').rstrip()
            properties[key] = value

        return properties

    def _add_to_all_properties(self, properties):
        for key in properties:
            self._all_properties.add(key)

    def get_all_properties(self):
        return self._all_properties

def main():  # {{{
    """Execute module in command line mode."""

    args = ArgumentParser(
        description="Parse feature list from http://geizhals.de and dump it as csv.",
        epilog=__doc__
    )
    args.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    args.add_argument(
        'file',
        help=u"raw test file file",
    )
    args.add_argument(
        '-w',
        '--wanted',
        help=u"Wanted property fields."
    )
    user_parms = args.parse_args()
    wanted_properties = ()
    if user_parms.wanted:
        wanted_properties = tuple(user_parms.wanted.decode('UTF-8').split(','))

    logging.basicConfig(
        format='# %(levelname)s: %(message)s',
        # level=logging.DEBUG,
        level=logging.INFO,
    )
    logging.info(u"Running %s", SCRIPT_URL)

    l2t_parser = ListToTable(
        user_parms.file,
        user_parms.file + u'.csv',
        wanted_properties=wanted_properties
    )

    logging.info(
        u"All properties: %s",
        u','.join(l2t_parser.get_all_properties())
    )

if __name__ == '__main__':
    from argparse import ArgumentError, ArgumentParser

    main()
# }}}
