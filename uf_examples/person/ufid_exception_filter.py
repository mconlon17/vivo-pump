#!/usr/bin/env/python

"""
    ufid_exception_filter.py -- remove ufids on an exception list
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp
import shelve
import sys

ufid_exception_shelve = shelve.open('ufid_exceptions.db')
ufid_exceptions = set(ufid_exception_shelve.keys())  # a set of ufids that will not be in the output
data_in = read_csv_fp(sys.stdin)
data_out = {}
remove_count = 0
for row, data in data_in.items():
    new_data = dict(data)
    if new_data['UFID'] in ufid_exceptions:
        new_data['remove'] = 'remove'
        remove_count += 1
    else:
        new_data['remove'] = ''
    data_out[row] = new_data
print >>sys.stderr, 'Remove count', remove_count
write_csv_fp(sys.stdout, data_out)
ufid_exception_shelve.close()





