#!/usr/bin/env/python

"""
    ufid_exception_filter.py -- remove ufids on an exception list
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv, write_csv
import shelve
import sys

ufid_exception_shelve = shelve.open('ufid_exceptions.db')
ufid_exceptions = set(ufid_exception_shelve.keys())  # a set of ufids that will not be in the output
data_in = read_csv(sys.stdin, delimiter='\t')
data_out = {}
for row, data in data_in.items():
    if data['UFID'] not in ufid_exceptions:
        data_out[row] = data
write_csv(sys.stdout, data_out, delimiter='\t')
ufid_exception_shelve.close()





