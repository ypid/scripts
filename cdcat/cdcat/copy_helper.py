#!/usr/bin/env python
# encoding: utf-8
# @author Robin Schneider <ypid23@aol.de>
# @licence GPLv3 <http://www.gnu.org/licenses/gpl.html>
#
"""
Implementation of the work flow explained here: http://superuser.com/a/717689
In short: Uses the database from cdcat to copy wanted files.
"""

# modules {{{
import os
import codecs
import logging

import gzip
import xml.etree.ElementTree as ET
# }}}

# module wide variables {{{
SCRIPT_URL = 'https://github.com/ypid/scripts/blob/master/cdcat/cdcat.py'
# }}}


class CopyHelper:  # {{{

    """
    Class which implements functions to parse a cdcat database and generate
    copy scripts based on it.
    """

    def __init__(
            self,
            directory_separator=os.path.sep,
            shell='sh',
            calc_size=False
    ):
        self._executing_shell_to_file_suffix = {
            'sh': 'sh',
            'cmd': 'bat',
        }
        self._executing_shell = shell
        self._calculate_size = calc_size
        self._directory_separator = directory_separator
        self.__name_of_base_path_variable = 'media_id_'
        self.__name_of_target_path_variable = 'target_path'
        self._base_filename = None
        self._generate_format = None
        # robocopy parameters {{{
        self._robocopy_parameter_string = '-s -r:2 -w:3' \
            + ' -log+:"target\\log-%date:~6,4%-%date:~0,2%-%date:~3,2%' \
            + ' _%time:~0,2%-%time:~3,2%-%time:~6,2%.log" -tee'
        # http://technet.microsoft.com/de-de/library/cc733145%28v=ws.10%29.aspx
        # -s:   Copies subdirectories. Note that this option excludes empty
        #       directories. (Empty directories are not consider as useful).
        # -r:<N>:   Specifies the number of retries on failed copies.
        #           The default value of N is 1,000,000 (one million retries).
        # -w:<N>:   Specifies the wait time between retries, in seconds.
        #           The default value of N is 30 (wait time 30 seconds).
        # -log+:<LogFile>:  Writes the status output to the log file
        #                   (appends the output to the existing log file).
        # -tee: Writes the status output to the console window,
        #       as well as to the log file.
        # }}}

    def parse_compressed_catalog_file(self, gzip_file, generate_format='git-annex'):
        """
        Parse cdcat database and generate the copy script using the specified
        programs (in generate_format).

        :param gzip_file: path to the gzipped XML file from cdcat.
        :param generate_format: list with the program which should be used in
            the copy script (default is git-annex).
        """

        self._base_filename = gzip_file
        if gzip_file[-4:] == '.hcf':
            self._base_filename = gzip_file[:-4]
        self._generate_format = generate_format
        gzip_file_fh = gzip.open(gzip_file, 'rb')
        xml_object = ET.ElementTree(ET.fromstring(gzip_file_fh.read()))
        gzip_file_fh.close()

        self._for_xml_object(xml_object)

    def parse_uncompressed_catalog_file(
            self, xml_file, generate_format='git-annex'):
        """
        Parse cdcat database and generate the copy script using the specified
        programs (in generate_format).

        :param gzip_file: path to the unzipped XML file from cdcat.
        :param generate_format: list with the program which should be used in
            the copy script (default is git-annex).
        """

        self._generate_format = generate_format
        xml_object = ET.parse(xml_file)

        self._for_xml_object(xml_object)

    def parse_catalog_file(
            self, catalog_file, generate_format='git-annex'):
        """
        Parse cdcat database and generate the copy script using the specified
        programs (in generate_format).

        :param catalog_file: path to the catalog file from cdcat (either gzipped or unzipped).
        :param generate_format: list with the program which should be used in
            the copy script (default is git-annex).
        """

        try:
            self.parse_compressed_catalog_file(catalog_file, generate_format)
        except IOError as error:
            try:
                self.parse_uncompressed_catalog_file(catalog_file, generate_format)
            except ET.ParseError as error:
                raise IOError('File {} could not be opened: {}'.format(catalog_file, error))

    def _for_xml_object(self, xml_object):
        self._start_line_comment_token = u'#'  # default is sh style comment
        if 'sh' == self._executing_shell:
            self._start_line_comment_token = u'#'
            logging.info(
                u'Generating copy script for sh (common Linux and Unix shell for scripting)'
            )
        if 'cmd' == self._executing_shell:
            self._start_line_comment_token = u'rem'
            logging.info(u'Generating copy script for Windows cmd')

        catalog = xml_object.getroot()
        self._for_catalog(catalog)

    def _for_catalog(self, catalog):
        logging.info(
            u'Parsing catalog called "%s" owned by "%s" …',
            catalog.attrib['name'],
            catalog.attrib['owner']
        )
        count = 1
        for media in catalog.findall('media'):
            self.__media_id = count
            self._for_media(media)
            count += 1

    def _for_media(self, media):
        logging.info(
            u'Parsing media: %s (type: %s, number: %d, time of import into db: %s)',
            media.attrib['name'],
            media.attrib['type'],
            int(media.attrib['number']),
            media.attrib['time']
        )
        self.__cur_copy_script_fh = codecs.open(
            '{}.{}.{}.{}'.format(
                self._base_filename,
                self.__media_id,
                self._generate_format,
                self._get_script_file_extention()
            ),
            'w',
            'UTF-8'
            )
        if 'sh' == self._executing_shell:
            self.__cur_copy_script_fh.write('#!/bin/sh\n')
        self.__cur_copy_script_fh.write(
            '{} This OS dependent copy script was generated by {}.\n'.format(
                self._start_line_comment_token,
                SCRIPT_URL
            )
        )
        if 'sys' in globals():
            self.__cur_copy_script_fh.write(
                '{} Command line options used for the script: "{}"\n'.format(
                    self._start_line_comment_token,
                    ' '.join(sys.argv)
                )
            )
        self.__cur_copy_script_fh.write(
            '{} You will need to change the base path to the media "{}"'.format(
                self._start_line_comment_token,
                media.attrib['name']
            )
            + ' and the target path.\n\n'
        )
        if 'git-annex' == self._generate_format:
            self.__cur_copy_script_fh.write(
                '{} Path to the base directory of the media'.format(
                    self._start_line_comment_token,
                )
                + ' (same as the one selected in cdcat for this media).\n\n'
            )
        else:
            self.__cur_copy_script_fh.write(
                '{}{}{}={}\n'.format(
                    'set ' if self._executing_shell == 'cmd' else '',
                    self.__name_of_base_path_variable,
                    self.__media_id,
                    media.attrib['name']
                )
            )
        if 'cmd' == self._executing_shell:
            self.__cur_copy_script_fh.write(
                'set {}=d:\\external_disk\\\n'.format(
                    self.__name_of_target_path_variable
                )
            )
        if 'git-annex' != self._generate_format:
            self.__cur_copy_script_fh.write(
                '{} The copy script will create one directory'
                + ' for each media under "{1}".\n'.format(
                    self._start_line_comment_token,
                    self._get_expandable_variable(
                        self.__name_of_target_path_variable
                    )
                )
            )
        self.__cur_copy_script_fh.write(
            '\n{} Do not change the following commands.'.format(
                self._start_line_comment_token
            )
            + ' They can be regenerated be the script after altering the database with cdcat'
            + ' (in case you want to select other files as listed here).\n'
        )

        self._for_dir(media, '', '', None)

        if 'cmd' == self._executing_shell:
            self.__cur_copy_script_fh.write('pause\n')

        self.__cur_copy_script_fh.write('\n')
        self.__cur_copy_script_fh.close()

    # helper functions {{{
    def _get_script_file_extention(self):
        """Returns the correct file extension the copy script as string."""
        return self._executing_shell_to_file_suffix[self._executing_shell]

    def _get_expandable_variable(self, name):
        """
        Returns the script language dependent variable which will expand to the
        base path of the source where the data is located.
        """
        if 'sh' == self._executing_shell:
            return '${%s%d}' % (name, self.__media_id)
        if 'cmd' == self._executing_shell:
            return '%%%s%d%%' % (name, self.__media_id)

    def _copy_node(self, node):
        category = node.find('category')
        if category is None:
            return None
        else:
            try:
                copy_priority = int(category.text)
            except ValueError:
                return False
            return copy_priority

    def _get_path(self, cur_path, node):
        if 'media' in node.tag:
            return ''
            # Media name is not file path.
        else:
            if not cur_path:
                return node.attrib['name']
            else:
                return self._directory_separator.join([
                    cur_path, node.attrib['name']
                ])
    # }}}

    # generate copy script entry for node {{{
    def _add_to_copy_list(
            self, base_path, cur_path, file_path, unwanted, node_type):
        unwanted = [item for item in unwanted if item is not None]
        node_path = cur_path if node_type == 'dir' else file_path
        source_node_path = self._directory_separator.join(
            [base_path, node_path])
        logging.debug(u'Include %s %s', node_type, node_type)
        if 'git-annex' == self._generate_format:
            unwanted = ['--exclude=\'%s\'' % item for item in unwanted]
            # print 'mkdir -p \'%s\' && pushd \'%s\'' % (cur_path, cur_path)
            # print 'git annex get \'%s\' %s' % (source_node_path, '
            # '.join(unwanted))
            self.__cur_copy_script_fh.write(
                'git annex get \'{}\' {}'.format(
                    node_path,
                    ' '.join(unwanted)
                )
            )
            # print 'git annex copy \'%s\' %s' % (node_path, ' '.join(unwanted))
            # print 'popd'
        if 'robocopy' == self._generate_format:
            unwanted = ['\'%s\'' % item for item in unwanted]
            if len(unwanted) != 0:
                logging.warning(
                    'robocopy does not support to exclude files or directories.'
                    + ' Directories(s) or file(s) "%s" will be copied although they where excluded.',
                    ' '.join(unwanted)
                )

            self.__cur_copy_script_fh.write(
                'robocopy "%s%s%s" "%s\\%s" %s\n' % (
                    self._get_expandable_variable(
                        self.__name_of_base_path_variable),
                    self._directory_separator, node_path,
                    self._get_expandable_variable(
                        self.__name_of_target_path_variable),
                    cur_path,
                    self._robocopy_parameter_string
                )
            )
    # }}}

    # for file {{{
    def _for_file(self, file_node, base_path, cur_path, implicit_wanted_node):
        file_path = self._get_path(cur_path, file_node)

        explicit_wanted_node = self._copy_node(file_node)
        wanted_node = explicit_wanted_node if explicit_wanted_node is not None else implicit_wanted_node

        if not wanted_node:
            # if explicit_wanted_node is False and implicit_wanted_node is True:
            #     return file_path
            logging.debug(u'Not file %s', file_path)
            return file_path
        else:
            if explicit_wanted_node and not implicit_wanted_node:
                self._add_to_copy_list(
                    base_path,
                    cur_path,
                    file_path, [], 'file')
            else:
                # File is already included from a upper directory.
                return None
    # }}}

    # for dir {{{
    def _for_dir(self, dir_node, base_path, cur_path, implicit_wanted_node):
        cur_path = self._get_path(cur_path, dir_node)
        explicit_wanted_node = self._copy_node(dir_node)
        if implicit_wanted_node is False and not explicit_wanted_node:
            logging.debug(u'Not dir %s (excluded from upper dir)', cur_path)
            return cur_path

        wanted_node = explicit_wanted_node if explicit_wanted_node is not None else implicit_wanted_node
        unwanted = []
        for directory_node in dir_node.findall('directory'):
            unwanted.append(
                self._for_dir(
                    directory_node,
                    base_path,
                    cur_path,
                    wanted_node))
        for file_node in dir_node.findall('file'):
            unwanted.append(
                self._for_file(
                    file_node,
                    base_path,
                    cur_path,
                    wanted_node))
        if wanted_node:
            self._add_to_copy_list(base_path, cur_path, None, unwanted, 'dir')
        if explicit_wanted_node is False:
            return cur_path
    # }}}
# }}}


def main():  # {{{
    """Execute module in command line mode."""

    args = argparse.ArgumentParser(
        description="Uses the database from cdcat to copy wanted files.",
        epilog="Implementation of the work flow explained here:"
        + " http://superuser.com/a/717689",
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
        help="cdcat database file",
    )
    args.add_argument(
        '-s',
        '--shell',
        choices=['cmd', 'sh'],
        default='sh',
        help="Specifies the interpreting shell and thous the environment.",
    )
    args.add_argument(
        '-m',
        '--method',
        choices=['robocopy', 'git-annex', 'test'],
        default='git-annex',
        help="Specifies the program to use."
        " If \"test\" was chosen a test script will be generated instead which checks if all selected files are available.",
    )
    args.add_argument(
        '-S',
        '--size',
        action='store_true',
        default=False,
        help="Calculate size of selected files.",
    )
    args.add_argument(
        '-u',
        '--summery',
        action='store_true',
        default=False,
        help="Show summery of the wanted files instead of creating copy scripts.",
    )
    args.add_argument(
        '-p',
        '--priority',
        action='store_true',
        default=False,
        help="Honor priority. Higher numbers are more important.",
    )
    user_parms = args.parse_args()

    logging.basicConfig(
        format='# %(levelname)s: %(message)s',
        # level=logging.DEBUG,
        level=logging.INFO,
    )
    logging.info(u"Running cdcat-parser: %s", SCRIPT_URL)

    copy_script = CopyHelper(
        # directory_separator='\\',
        shell=user_parms.shell,
        calc_size=user_parms.size,
    )
    copy_script.parse_catalog_file(
        user_parms.file,
        generate_format=user_parms.method,
    )

if __name__ == '__main__':
    import argparse
    import sys

    main()
# }}}
