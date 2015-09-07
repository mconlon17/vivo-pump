#!/usr/bin/env/python

"""
    gen_dates.py -- generate dates for inclusion in VIVO
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

from datetime import datetime
from dateutil.relativedelta import relativedelta

out_file = open('dates.txt', "w")
print >>out_file, "uri\tPrecision\tDate"

#   Generate years

for year in range(1800, 2051):
    date_string = str(year) + "-01-01T00:00:00"
    print >>out_file, "\t" + "y" + "\t" + date_string

#   Generate year month

current_date = datetime(1800, 1, 1)
end_date = datetime(2050, 12, 31)
while current_date <= end_date:
    date_string = current_date.isoformat()
    print >>out_file, "\t" + "ym" + "\t" + date_string
    current_date += relativedelta(months=+1)

#   Generate year month day

current_date = datetime(1800, 1, 1)
end_date = datetime(2050, 12, 31)
while current_date <= end_date:
    date_string = current_date.isoformat()
    print >>out_file, "\t" + "ymd" + "\t" + date_string
    current_date += relativedelta(days=+1)

out_file.close()
