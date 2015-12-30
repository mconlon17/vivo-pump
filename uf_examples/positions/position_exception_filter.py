#!/usr/bin/env/python

"""
    position_exception_filter.py -- positions on the exception list will be excluded
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import shelve
import sys

from pump.vivopump import read_csv_fp, write_csv_fp

position_exception_shelve = shelve.open('position_exceptions.db')
position_exceptions = set(position_exception_shelve.keys())  # a set of positions that will not have data updates
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, "In", len(data_in)
data_out = {}
exclude_count = 0
for row, data in data_in.items():
    new_data = dict(data)
    if new_data['JOBCODE_DESCRIPTION'] in position_exceptions:
        exclude_count += 1
    else:
        data_out[row] = new_data
print >>sys.stderr, 'Exclude count', exclude_count
print >>sys.stderr, "Out", len(data_out)
write_csv_fp(sys.stdout, data_out)
position_exception_shelve.close()





