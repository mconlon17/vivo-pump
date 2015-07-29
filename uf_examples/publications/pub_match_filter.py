#!/usr/bin/env/python

"""
    pub_match_filter.py -- find the pubs in VIVO, and match them by title to the pubs
    in the source.

    There are two inputs:
    1. pubs in VIVO.  Keyed by title
    2. pubs in the source.  Keyed by title

    There are three cases
    1. pub in VIVO and in source => add to update data with uri
    1. pub in VIVO, not in source => nothing to do
    1. pub not in VIVO, is in source => Add to update data with blank uri (to be assigned during update)

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, get_vivo_pubs
import sys

data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
vivo_pubs = get_vivo_pubs()  # get dictionary of pub uri keyed by simplified  name
print >>sys.stderr, 'VIVO pubs', len(vivo_pubs)
print >>sys.stderr, vivo_pubs

for row, data in data_in.items():
    data_out[row] = data
    if data['issn'] not in vivo_pubs:  # name is not vivo.  These are the ones to add
        data_out[row]['uri'] = ''
    else:
        data_out[row]['uri'] = vivo_pubs[data['issn']]

print >>sys.stderr, 'data out', len(data_out)
write_csv_fp(sys.stdout, data_out)





