#!/usr/bin/env/python

"""
    merge_filter.py -- find the courses in VIVO, and match them to the courses in the source.  They
    must match on ccn

    There are two inputs:
    1. Courses in VIVO.  Keyed by ccn
    2. UF courses in the source.  Keyed the same.

    There are three cases
    1. Course in VIVO and in Source => Update VIVO from source
    1. Course in VIVO, not in source => nothing to do
    1. Course not in VIVO, is in source => Add to VIVO

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.02"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp, get_vivo_ccn, get_parms

parms = get_parms()
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
vivo_courses = get_vivo_ccn(parms)  # get dictionary of course uri keyed by ccn
print >>sys.stderr, 'VIVO courses', len(vivo_courses)

for row, data in data_in.items():
    new_data = dict(data)
    if data['ccn'] in vivo_courses:  # ccn is in vivo and source
        new_data['uri'] = vivo_courses[data['ccn']]
    else:  # key is in source, not in vivo
        new_data['uri'] = ''
    data_out[row] = new_data

print >>sys.stderr, 'data out', len(data_out)
write_csv_fp(sys.stdout, data_out)





