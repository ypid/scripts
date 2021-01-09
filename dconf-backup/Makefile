# SPDX-FileCopyrightText: 2017 Robin Schneider <ypid@riseup.net>
#
# SPDX-License-Identifier: AGPL-3.0-only

.PHONY : backup
backup:
	./dconf_backup_all
	git commit --all --message "Auto commit."

.PHONY : restore
restore:
	./dconf_restore_all
