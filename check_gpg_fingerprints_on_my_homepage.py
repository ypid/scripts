#!/usr/bin/env python
# encoding: utf-8
## @author Robin Schneider <ypid23@aol.de>
## @licence GPLv3 <http://www.gnu.org/licenses/gpl.html>
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation version 3 of the License.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''Check the GPG fingerprints on my homepage if there are the correct ones.'''

# modules {{{
import re, sys
import subprocess
import logging
import codecs
from HTMLParser import HTMLParser
import urllib2
from termcolor import colored
# }}}

logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.DEBUG,
    # level=logging.INFO,
)

PAGES_WITH_GPG_KEYS = {
    'blog': 'ypid.wordpress.com/uber-mich',
    'osm-wiki': 'wiki.openstreetmap.org/wiki/User:Ypid'
        }
PROTOCOLS=[ 'http', 'https' ]
gpg_list_keys_command = [ 'gpg', '--list-public-keys', '--fingerprint', 'Robin Schneider (Automatic Signing Key) <ypid23@aol.de>', 'Robin Schneider (Release Signing Key) <ypid23@aol.de>', 'Robin `ypid` Schneider <ypid23@aol.de>' ]

## helper functions {{{
def make_clean(string, is_html):
    '''Workaround for HTMLParser. Not sure why but if an HTML entity is contained in the parsed HTML the HTMLParser does not work probably.'''
    if is_html:
        return string.replace('&lt;', '**EmailStart**').replace('&gt;', '**EmailEnd**')
    else:
        return string.replace('<', '**EmailStart**').replace('>', '**EmailEnd**')

def reverse_clean(string):
    return string.replace('**EmailStart**', '<').replace('**EmailEnd**', '>')

def sort_string_lines(string):
    array_of_lines=[]
    for line in string.split('\n'):
        line = line.strip()
        if line != '':
            array_of_lines.append(line.strip())
    return sorted(array_of_lines)
## }}}

## get trusted fingerprints from my machine {{{
gpg_public_keys_from_my_machine = u''

process = subprocess.Popen(gpg_list_keys_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
while True:
    out = process.stdout.read(1)
    if out == '' and process.poll() != None:
        break
    if out != '':
        gpg_public_keys_from_my_machine += out.encode('utf-8')
gpg_public_keys_from_my_machine_array = [make_clean(line, False) for line in sort_string_lines(gpg_public_keys_from_my_machine)]
## }}}

## HTML parser {{{
class MyHTMLParser(HTMLParser):
    _in_pre = False
    pre_data = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self._in_pre = True
    def handle_endtag(self, tag):
        if tag == 'pre':
            self._in_pre = False
    def handle_data(self, data):
        if self._in_pre:
           self.pre_data = data
## }}}

def compate_with_html_page(html):
    number_ok = 0
    parser = MyHTMLParser()
    parser.feed(make_clean(html, True))
    gpg_public_keys_from_web_pages_array = sort_string_lines(parser.pre_data)

    max_len = max(len(gpg_public_keys_from_web_pages_array), len(gpg_public_keys_from_my_machine_array))

    len_equal = len(gpg_public_keys_from_web_pages_array) == len(gpg_public_keys_from_my_machine_array)

    if not len_equal:
        logging.warning('Lengths for the trusted lines and the lines form the web differ (max %d).' % max_len)

    for idx in range(max_len):
        trusted_line = gpg_public_keys_from_my_machine_array[idx]

        if trusted_line == None:
            if trusted_line != None:
                logging.warning('Line available locally but not upstream: %s' % trusted_line)
            # if line != None:
                # logging.warning('Line available upstream but not locally: %s' % line)
        elif trusted_line not in gpg_public_keys_from_web_pages_array:
            logging.error('%s\n%s%s' % (
                'String at line %d was not found remotely:' % idx,
                '\tExpected: "%s"' % reverse_clean(trusted_line),
                '\n\tGot:      "%s"' % reverse_clean(gpg_public_keys_from_web_pages_array[idx]) if len_equal else ''
                )
            )
        else:
            number_ok += 1
    logging.info('%d lines are equal out of %d' % (number_ok, max_len))
    return max_len - number_ok

lines_not_matching = 0
# with codecs.open('/tmp/tmp.tyUKNB362M/blog.http.html', 'r', 'UTF-8') as content_file:
with codecs.open('/tmp/web', 'r', 'UTF-8') as content_file:
    content = content_file.read()
    lines_not_matching += compate_with_html_page(content)

for proto in PROTOCOLS:
    for page_name in PAGES_WITH_GPG_KEYS:
        url='%s://%s' % (proto, PAGES_WITH_GPG_KEYS[page_name])
        # content = urllib2.urlopen(url).read().decode('utf-8')
        # print type(content)
        # compate_with_html_page(content)
        break
    break
