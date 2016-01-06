#!/usr/bin/env/python

"""
    uri_exception_filter.py -- uris on the exception list will not have data updates
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import shelve
import sys

from pump.vivopump import read_csv_fp, write_csv_fp

uri_exception_shelve = shelve.open('uri_exceptions.db')
uri_exceptions = set(uri_exception_shelve.keys())  # a set of uris that will not have data updates
data_in = read_csv_fp(sys.stdin)
data_out = {}
exempt_count = 0
for row, data in data_in.items():
    new_data = dict(data)
    if 'uri' in new_data and new_data['uri'] in uri_exceptions:
        for name in new_data.keys():
            if name != 'uri' and name != 'UFID':
                new_data[name] = ''
        exempt_count += 1
    data_out[row] = new_data
print >>sys.stderr, 'Exempt count', exempt_count
write_csv_fp(sys.stdout, data_out)
uri_exception_shelve.close()





