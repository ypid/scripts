# dconf-backup

Very simple shell scripts to backup and restore parts of your dconf database.

## Quick start

```Shell
## Creates and marks /org/gnome/evince to be backuped up to the file org.gnome.evince.dump
./dconf_backup org.gnome.evince.dump

## Updates all present backup files.
./dconf_backup_all

## Restores all backup files (applies the changes to the dconf database).
./dconf_restore_all
```
