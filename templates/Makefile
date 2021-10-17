# vim: foldmarker={{{,}}}:foldmethod=marker

# SPDX-FileCopyrightText: 2021 Robin Schneider <ypid@riseup.net>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

SHELL ?= /bin/bash -o nounset -o pipefail -o errexit
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

#-# Help {{{
#-# https://stackoverflow.com/a/26339924/2239985
.PHONY: list
list:
	@if command -v mmake >/dev/null 2>&1; then \
		mmake help; \
	else \
		echo "This Makefile has the following targets:"; \
		$(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) / 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | sed 's/^/    /' | sort; \
	fi
#-# }}}

test:
	@echo "Do something." 1>&2
