# encoding: utf-8
import os
import codecs
import re
import subprocess

import unittest
import logging
logging.basicConfig(
    format='# %(levelname)s: %(message)s',
    # level=logging.DEBUG,
    level=logging.ERROR,
)

from cdcat.copy_helper import CopyHelper

BASE_DIR = u'tests'
DIRECTORY_OF_EXPECTED_SCRIPTS = u'expected'
CATALOG_FILE_SELECTED = u'files_selected'
CATALOG_FILE_NOT_SELECTED = u'no_selected_files'

class TestCdcat(unittest.TestCase):

    def test_compare_with_expected(self):

        dir_of_expected_scripts = os.path.join(
            BASE_DIR,
            DIRECTORY_OF_EXPECTED_SCRIPTS
        )
        for dirname, dirnames, filenames in os.walk(dir_of_expected_scripts):
            for filename in filenames:
                suffix = filename.replace(CATALOG_FILE_SELECTED + '.', '')
                suffix_re = re.match(
                    r'(?P<media_id>[0-9]+)'
                    r'\.(?P<method>[a-z-]+)'
                    r'\.(?P<file_extention>[a-z]+)$',
                    suffix
                )
                if not suffix_re:
                    logging.warning("No match for {}".format(filename))
                    continue
                media_id = suffix_re.group('media_id')
                # if media_id != '1':
                #     continue
                logging.info(filename)

                method = suffix_re.group('method')
                file_extention = suffix_re.group('file_extention')
                base_filename = os.path.join(BASE_DIR, CATALOG_FILE_SELECTED)
                expected_script_filename = os.path.join(dirname, filename)

                copy_helper = CopyHelper()
                file_suffix_to_executing_shell = {v:k for k, v in copy_helper._executing_shell_to_file_suffix.items()}
                copy_helper._executing_shell = file_suffix_to_executing_shell[file_extention]
                for catalog_filename in [u'hcf', u'hcf.unp']:
                    catalog_filename = base_filename + '.' + catalog_filename
                    copy_helper.parse_catalog_file(
                        catalog_filename,
                        generate_format=method
                    )
                    generated_script_filename = '{}.{}.{}.{}'.format(
                        copy_helper._base_filename,
                        media_id,
                        method,
                        file_extention
                    )
                    try:
                        output = subprocess.check_output(
                            [
                                'diff',
                                generated_script_filename,
                                expected_script_filename
                            ]
                        )
                        if output:
                            print output
                    except subprocess.CalledProcessError as error:
                        print error.output
                        return False

if __name__ == "__main__":
    unittest.main()
