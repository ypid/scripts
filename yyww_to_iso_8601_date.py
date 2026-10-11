#!/usr/bin/env python3
"""
Convert a YYWW command-line parameter into an ISO 8601 date string.

The input consists of:
  YY = two-digit year (2000 to 2099)
  WW = ISO 8601 calendar week (01 to 53)

The output is the Monday of the specified ISO calendar week,
formatted as YYYY-MM-DD.

Example:
  ./date.py 2533
  2025-08-11
"""
import sys
from datetime import date

yyww = sys.argv[1]
year, week = 2000 + int(yyww[:2]), int(yyww[2:])
print(date.fromisocalendar(year, week, 1).isoformat())
