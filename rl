#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2019-2020 Robin Schneider <ypid@riseup.net>
#
# SPDX-License-Identifier: AGPL-3.0-only

set -o nounset -o pipefail -o errexit

# rl: read log
# journalctl wrapper with nice output format and colors based on log event severity.
# The order is for human consumption only so they are just based on RFC 5424 (without being compliant) and the default journalctl short-iso format.
# The syslog severity is added which is missing in common log formats or not human readable (RFC 5424).
# Proper RFC 3339 date format. The format for the additional weekday was taken from systemd.time(7).
# The colors are made up by ypid because I could not find a proper standard.
# Ref: https://serverfault.com/questions/59262/bash-print-stderr-in-red-color/502019#502019
# Ref: https://serverfault.com/questions/801514/systemd-default-log-output-format
# Ref: https://github.com/systemd/systemd/issues/14515

export LC_ALL=C.UTF-8

# shellcheck disable=SC2016
command journalctl "$@" -o json \
    | jq --unbuffered --raw-output '"echo \(.PRIORITY|tonumber|@sh) \"$(date --date @\((._SOURCE_REALTIME_TIMESTAMP // .__REALTIME_TIMESTAMP) |tonumber | ./ 1000000 | tostring) '\''+%a %F %T%:z'\'')\" \(._HOSTNAME|@sh) \(.SYSLOG_IDENTIFIER|@sh): \(.MESSAGE | gsub("\n"; "\n    ") | @sh) "' \
    | sh \
    | perl -e 'my $c_to_sev = {0 => "48;5;9", 1 => "48;5;5", 2 => "38;5;9", 3 => "38;5;1", 4 => "38;5;5", 5 => "38;5;2", 6 => "38;5;2"}; while (<>) { s#^(([0-6])(?: [^ ]+){5})(.*)#\e[$c_to_sev->{$2}m$1\e[m$3#; print; }'
