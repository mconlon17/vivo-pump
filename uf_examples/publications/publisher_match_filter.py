#!/usr/bin/env/python

"""
    publisher_match_filter.py -- find the publishers in VIVO, and match them by name to the publishers
    in the source.

    There are two inputs:
    1. publishers in VIVO.  Keyed by simplified name
    2. publishers in the source.  Keyed by simplified name

    There are three cases
    1. publisher in VIVO and in Source => nothing to do
    1. publisher in VIVO, not in source => nothing to do
    1. publisher not in VIVO, is in source => Add to VIVO

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015"
__license__ = "New BSD License"
__version__ = "0.02"

from vivopump import read_csv_fp, write_csv_fp, get_vivo_publishers, key_string
import sys

data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
data_out = {}
row_out = 0
vivo_publishers = get_vivo_publishers()  # get dictionary of publisher uri keyed by simplified  name
print >>sys.stderr, 'VIVO publishers', len(vivo_publishers)
print >>sys.stderr, vivo_publishers

for row, data in data_in.items():
    key = key_string(data['name'])
    if key not in vivo_publishers:  # name is not vivo.  These are the ones to add
        row_out += 1
        data_out[row_out] = data

print >>sys.stderr, 'data out', len(data_out)
write_csv_fp(sys.stdout, data_out)





