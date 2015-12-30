#!/usr/bin/env/python

"""
    merge_filter.py -- find the positions in VIVO, and match them to the positions in the source.  They
    must match on ufid, deptid, hr-title and start date.

    There are two inputs:
    1. positions in VIVO.  Keyed by ufid, deptid, hr-title, start-date. A concatenated key.
    2. UF positions in the source.  Keyed the same.

    There are three cases
    1. Position in VIVO and in Source => Update VIVO from source
    1. Position in VIVO, not in source => nothing to do
    1. Position not in VIVO, is in source => Add to VIVO

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.02"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp, get_vivo_positions, get_parms

parms = get_parms
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
vivo_positions = get_vivo_positions(parms)  # get dictionary of position uri keyed by ufid, deptid, hr_title, start_date
print >>sys.stderr, 'VIVO positions', len(vivo_positions)

for row, data in data_in.items():
    key = ';'.join([data['UFID'], data['DEPTID'], data['hr_title'], data['START_DATE']])
    data_out[row] = data
    if key in vivo_positions:  # ufid is in vivo and source
        data_out[row]['uri'] = vivo_positions[key]
    else:  # key is in source, not in vivo
        data_out[row]['uri'] = ''

print >>sys.stderr, 'data out', len(data_out)
write_csv_fp(sys.stdout, data_out)





