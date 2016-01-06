#!/usr/bin/env/python

"""
    merge_filter.py -- merge the position data with the data in VIVO.  Oh my.  Add a column for uri, add a
    column for uf current, add a column for remove

    There are two inputs:
    1. UF people in VIVO, keyed by UFID
    2. UF people on the pay list.  Keyed by UFID

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.02"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp, get_vivo_ufid, get_parms

parms = get_parms()
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
vivo_ufid = get_vivo_ufid(parms)  # get dictionary of uri keyed by ufid
vivo_ufids = vivo_ufid.keys()
print >>sys.stderr, 'VIVO ufid', len(vivo_ufid)
source_ufid = [data_in[x]['UFID'] for x in data_in]
print >>sys.stderr, 'Source ufid', len(source_ufid)

vivo_data = data_in[data_in.keys()[0]]  # Grab a row, any row

#   Process ufid in VIVO and in Source

for row, data in data_in.items():
    ufid = data['UFID']
    if ufid in vivo_ufids:  # ufid is in vivo and source
        data_out[row] = dict(data)
        data_out[row]['uri'] = vivo_ufid[ufid]
        data_out[row]['current'] = 'yes'
    else:  # ufid is in source, not in vivo
        data_out[row] = dict(data)
        data_out[row]['uri'] = ''
        data_out[row]['current'] = 'yes'

#   Some ufids are in VIVO and not in the source data (mostly people who have left the university and are
#   no longer being paid).  These people need to be in the update data so that their contact data and other
#   attributes can be checked and updated.  Their data starts as blank -- no update.  But they may gain values
#   through additional filtering operations

row_number = max(data_in.keys())  # vivo will continue numbering rows from here
blank_data = dict(zip(vivo_data.keys(), ['' for x in vivo_data.keys()]))
print >>sys.stderr, blank_data
print >>sys.stderr, vivo_ufid
for ufid, uri in vivo_ufid.items():
    if ufid not in source_ufid:
        row = dict(blank_data)
        row['UFID'] = ufid
        row['uri'] = uri
        row['current'] = 'no'
        row_number += 1
        data_out[row_number] = row
        print >>sys.stderr, row_number, data_out[row_number]

print >>sys.stderr, 'data out', len(data_out)
write_csv_fp(sys.stdout, data_out)





