#!/usr/bin/env/python

"""
    ufid_exception_filter.py -- ufids on the exception list will not have data updates
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import shelve
import sys

from pump.vivopump import read_csv_fp, write_csv_fp

ufid_exception_shelve = shelve.open('ufid_exceptions.db')
ufid_exceptions = set(ufid_exception_shelve.keys())  # a set of ufids that will not have data updates
data_in = read_csv_fp(sys.stdin)
data_out = {}
exempt_count = 0
for row, data in data_in.items():
    new_data = dict(data)
    if new_data['UFID'] in ufid_exceptions:
        for name in new_data.keys():
            if name != 'uri' and name != 'UFID':
                new_data[name] = ''
        exempt_count += 1
    data_out[row] = new_data
print >>sys.stderr, 'Exempt count', exempt_count
write_csv_fp(sys.stdout, data_out)
ufid_exception_shelve.close()





