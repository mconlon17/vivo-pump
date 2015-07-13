#!/usr/bin/env/python

"""
    match_journals_filter.py -- find the journals in VIVO, and match them by issn to the journals
    in the source.

    There are two inputs:
    1. journals in VIVO.  Keyed by ISSN
    2. journals in the source.  Keyed by ISSN

    There are three cases
    1. journal in VIVO and in Source => add to update data with uri
    1. journal in VIVO, not in source => nothing to do
    1. journal not in VIVO, is in source => Add to update data with blank uri (to be assigned during update)

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, get_vivo_journals
import sys

data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
vivo_journals = get_vivo_journals()  # get dictionary of journal uri keyed by simplified  name
print >>sys.stderr, 'VIVO journals', len(vivo_journals)
print >>sys.stderr, vivo_journals

for row, data in data_in.items():
    data_out[row] = data
    if data['issn'] not in vivo_journals:  # name is not vivo.  These are the ones to add
        data_out[row]['uri'] = ''
    else:
        data_out[row]['uri'] = vivo_journals[data['issn']]

print >>sys.stderr, 'data out', len(data_out)
write_csv_fp(sys.stdout, data_out)





