<!--
SPDX-FileCopyrightText: 2018 Robin Schneider <ypid@riseup.net>

SPDX-License-Identifier: AGPL-3.0-only
-->

# Public webcam download script

Intended for downloading/archiving pictures taken by (public) webcams where you can download a (JPEG) image which is usually updated every minute.

I checked out https://github.com/jflalonde/WebcamDownload.git and did an extensive Internet search.
Also went through all results in https://github.com/search?q=webcam+url&type=Repositories

In the end, I wrote my own scripts. Simple shell scripts still rule.

## Cron example

```
* 08-20 * * * ~/path/to/scripts/load_url 'https://domain/path/webcam.jpg' 'camera_id' ~/webcams
23 4    * * * ~/path/to/scripts/remove_duplicates ~/webcams
```
