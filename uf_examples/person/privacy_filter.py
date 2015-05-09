#!/usr/bin/env/python

"""
    privacy_filter.py -- remove ufids with privacy protection, or that can not be found in the privacy data
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp
import shelve
import sys

privacy_shelve = shelve.open('privacy.db')
privacy_ufids = set(privacy_shelve.keys())  # a set of ufids that have privacy information
print len(privacy_ufids)
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
for row, data in data_in.items():
    if data['UFID'] in privacy_ufids:  # must have privacy information
        if privacy_shelve[data['UFID']]['UF_SECURITY_FLG'] == 'N' and privacy_shelve[data['UFID']][
                'UF_PROTECT_FLG'] == 'N':
            data_out[row] = data
        else:
            print >>sys.stderr, data['UFID'], 'protected.  Will not be added to VIVO'
    else:
        print >>sys.stderr, data['UFID'], 'not found in privacy data.  Will not be added to VIVO'
print >>sys.stderr, len(data_out)
write_csv_fp(sys.stdout, data_out)
privacy_shelve.close()





