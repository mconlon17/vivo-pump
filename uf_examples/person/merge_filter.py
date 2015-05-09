#!/usr/bin/env/python

"""
    merge_filter.py -- merge the position data with the data in VIVO.  Oh my.  Add a column for uri, add a
    column for uf current


    There are two inputs:
    1. UF people in VIVO, keyed by UFID
    2. UF people on the pay list.  Keyed by UFID

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, get_vivo_ufid
import sys


data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
vivo_ufid = get_vivo_ufid()  # get dictionary of uri keyed by ufid
vivo_ufids = vivo_ufid.keys()
print >>sys.stderr, 'VIVO ufid', len(vivo_ufid)
data_in = read_csv_fp(sys.stdin, delimiter='|')
source_ufid = [data_in[x]['UFID'] for x in data_in]
print >>sys.stderr, 'Source ufid', len(source_ufid)

for row, data in data_in.items():
    ufid = data['UFID']
    if ufid in vivo_ufids:
        data_out[row] = data
        data_out['uri'] = vivo_ufid[ufid]
        data_out['CURRENT'] = 'yes'
    else:
        data_out[row] = data
        data_out['uri'] = ''
        data_out['CURRENT'] = 'no'

print >>sys.stderr, len(data_out)
write_csv_fp(sys.stdout, data_out)





