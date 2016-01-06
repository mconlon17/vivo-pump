#!/usr/bin/env/python

"""
    privacy_filter.py -- remove ufids with privacy protection, or that can not be found in the privacy data
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import shelve
import sys

from pump.vivopump import read_csv_fp, write_csv_fp

privacy_shelve = shelve.open('privacy.db')
privacy_ufids = set(privacy_shelve.keys())  # a set of ufids that have privacy information
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, "Privacy start", len(data_in)
okay = 0
protected = 0
not_found = 0
data_out = {}
for row, data in data_in.items():
    if data['UFID'] in privacy_ufids:  # must have privacy information
        if privacy_shelve[data['UFID']]['UF_SECURITY_FLG'] == 'N' and privacy_shelve[data['UFID']][
                'UF_PROTECT_FLG'] == 'N':
            data_out[row] = data
            okay += 1
        else:
            protected += 1
    else:
        not_found +=1
print >>sys.stderr, "Okay", okay
print >>sys.stderr, "Protected", protected
print >>sys.stderr, "Not Found", not_found
print >>sys.stderr, "Privacy End", len(data_out)
write_csv_fp(sys.stdout, data_out)
privacy_shelve.close()





