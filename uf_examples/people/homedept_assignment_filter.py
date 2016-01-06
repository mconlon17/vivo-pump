#!/usr/bin/env/python

"""
    homedept_assignment_filter.py -- for home departments matched to patterns in an exception file, assign new
    home departments as indicated in the exception file
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import shelve
import sys
import re

from pump.vivopump import read_csv_fp, write_csv_fp

homedept_shelve = shelve.open('deptid_exceptions.db')
data_in = read_csv_fp(sys.stdin)
data_out = {}
reassign_count = 0
for row, data in data_in.items():
    new_data = dict(data)

    # check each pattern

    for pattern_string, action in homedept_shelve.items():
        pattern = re.compile(pattern_string)
        if pattern.search(new_data['HOME_DEPT']) is not None:
            new_data['HOME_DEPT'] = action['assigned_deptid']
            print >>sys.stderr, "Reassign from", data['HOME_DEPT'], 'to', new_data['HOME_DEPT']
            reassign_count += 1
    data_out[row] = new_data
print >>sys.stderr, 'Reassign count', reassign_count
write_csv_fp(sys.stdout, data_out)
homedept_shelve.close()





