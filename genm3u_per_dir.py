#!/usr/bin/env python
# encoding: utf-8
"""Script to generate m3u playlist files for the current directory."""
# @author Robin Schneider <ypid23@aol.de>
# @licence GPLv3 <http://www.gnu.org/licenses/gpl.html>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import codecs

import fnmatch

AUIDIO_FILE_GLOB = u'*.mp3'

for root, dirnames, filenames in os.walk(u'.'):
    if fnmatch.filter(filenames, AUIDIO_FILE_GLOB):
        m3u_fh = codecs.open(os.path.join(root, 'playlist.m3u'), 'w', 'UTF-8')
    for filename in fnmatch.filter(filenames, AUIDIO_FILE_GLOB):
        m3u_fh.write(u'{}\n'.format(filename))
        # print filename
    if 'm3u_fh' in locals():
        m3u_fh.close()
