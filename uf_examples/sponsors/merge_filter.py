#!/usr/bin/env/python

"""
    merge_filter.py -- find the sponsors in VIVO, and match them to the sponsors in the source.  They
    must match on sponsorid

    There are two inputs:
    1. sponsors in VIVO.  Keyed by sponsorid
    2. UF sponsors in the source.  Keyed the same.

    There are three cases
    1. sponsor in VIVO and in Source => Update VIVO from source
    1. sponsor in VIVO, not in source => nothing to do
    1. sponsor not in VIVO, is in source => Add to VIVO

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.02"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp, get_vivo_sponsorid, get_parms

parms = get_parms()
if parms['verbose']:
    print >>sys.stderr, parms
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
vivo_sponsors = get_vivo_sponsorid(parms)  # get dictionary of sponsor uri keyed by sponsorid
print >>sys.stderr, 'VIVO sponsors', len(vivo_sponsors)

for row, data in data_in.items():
    new_data = dict(data)
    if data['sponsorid'] in vivo_sponsors:  # sponsorid is in vivo and source
        new_data['uri'] = vivo_sponsors[data['sponsorid']]
    else:  # key is in source, not in vivo
        new_data['uri'] = ''
    data_out[row] = new_data

print >>sys.stderr, 'data out', len(data_out)
write_csv_fp(sys.stdout, data_out)





