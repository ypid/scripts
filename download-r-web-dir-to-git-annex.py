#!/usr/bin/env python
# encoding: utf-8
# Download directory listing containing specified files with git-annex.

# modules {{{
import logging, sys, re
import urllib2
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

# }}}

class Parser():
    # def __init__(self):

    def parse(self, url, file_regex = r'\.mp3\Z'):
        self._file_regex = file_regex

        self._for_dir(url)

    def _for_dir(self, url):
        html_page = urllib2.urlopen(url)
        soup = BeautifulSoup(html_page)
        for link in soup.findAll('a'):
            if link.get('href') != '../':
                full_url = '%s%s' % (url, link.get('href'))
                self._for_dir_with_files(full_url)

    def _for_dir_with_files(self, url):
        html_page = urllib2.urlopen(url)
        soup = BeautifulSoup(html_page)
        for link in soup.findAll('a', attrs={'href': re.compile(self._file_regex)}):
            if link.get('href') != '../':
                full_url = '%s%s' % (url, link.get('href'))
                print 'git annex addurl --file=\'%s\' \'%s\'' % (link.string, full_url)

# main {{{
if __name__ == '__main__':
    if len(sys.argv) > 2:
        url = sys.argv[1]
        file_regex = sys.argv[2]
    else:
        logging.error('Not enough parameters.'
                + ' 1. Base URL'
                + ' 2. File regex to get.'
                )
        sys.exit(1)

    parser = Parser()

    parser.parse(url, file_regex)

# }}}
