#!/usr/bin/env/python

"""
    unique_ccn_filter.py -- remove duplicate ccn
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp

data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, "Input rows", len(data_in)
data_out = {}
ccn_out = set()
for row, data in data_in.items():
    new_data = dict(data)
    if data['ccn'] not in ccn_out:
        data_out[row] = new_data
        ccn_out.add(data['ccn'])
print >>sys.stderr, "Output rows", len(data_out)
write_csv_fp(sys.stdout, data_out)





