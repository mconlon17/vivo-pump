#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
publisher_match_filter.py -- find the publishers in VIVO, and match them by
name to the publishers in the source.

There are two inputs:
    1. publishers in VIVO.  Keyed by simplified name
    2. publishers in the source.  Keyed by simplified name

There are three cases:
    1. publisher in VIVO and in Source => nothing to do
    2. publisher in VIVO, not in source => nothing to do
    3. publisher not in VIVO, is in source => Add to VIVO
"""
__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.02"

import sys

from disambiguate.utils import print_err
from pump.vivopump import read_csv_fp, write_csv_fp, get_vivo_publishers, get_parms,\
    key_string

parms = get_parms()
data_in = read_csv_fp(sys.stdin)
print_err('total input publishers: {}'.format(len(data_in)))

data_out = {}

# get dictionary of publisher uri keyed by simplified  name
vivo_publishers = get_vivo_publishers(parms)
print_err('total VIVO publishers: {}'.format(len(vivo_publishers)))
# print_err(vivo_publishers)

row_out = 0

for row, data in data_in.items():
    if 0 == row_out:
        # copy the header line so we don't end up with an empty file
        data_out[row_out] = data
        row_out += 1
        continue

    key = key_string(data['name'])

    if key not in vivo_publishers:
        # name is not vivo.  These are the ones to add
        data_out[row_out] = data
        row_out += 1
        print_err("key {} will be added to vivo: {}".format(key, data))

print_err('total rows in data_out: {}'.format(len(data_out)))
write_csv_fp(sys.stdout, data_out)
