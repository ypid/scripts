#!/bin/sh
# This OS dependent copy script was generated by https://github.com/ypid/scripts/blob/master/cdcat/cdcat.py.
# You will need to change the base path to the media "icedove" and the target path.

# Path to the base directory of the media (same as the one selected in cdcat for this media).


# Do not change the following commands. They can be regenerated be the script after altering the database with cdcat (in case you want to select other files as listed here).
git annex get 'chrome/icons/default/default24.png' git annex get 'defaults/pref' git annex get 'extensions/{972ce4c6-7e08-4474-a285-3208198ce6fd}' --exclude='extensions/{972ce4c6-7e08-4474-a285-3208198ce6fd}/install.rdf'