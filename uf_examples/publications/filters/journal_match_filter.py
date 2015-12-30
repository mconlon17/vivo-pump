#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
journal_match_filter.py -- find the journals in VIVO, and match them by issn to
    the journals in the source.

There are two inputs:
    1. journals in VIVO kyed by ISSN
    2. journals in the source keyed by ISSN

There are three cases:
    1. journal in VIVO and in Source => add to update data with uri
    2. journal in VIVO, not in source => nothing to do
    3. journal not in VIVO, is in source => Add to update data with blank uri
    (to be assigned during update)
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys

from disambiguate.utils import print_err
from pump.vivopump import read_csv_fp, write_csv_fp, get_vivo_journals, get_parms

parms = get_parms()
data_in = read_csv_fp(sys.stdin)
print_err("Input data length: {}".format(len(data_in)))

data_out = {}

# get dictionary of journal uri keyed by
# International Standard Serial Numbers (ISSN)
vivo_journals = get_vivo_journals(parms)
print_err('There are {} journals in VIVO'.format(len(vivo_journals)))
# print_err(vivo_journals)

for row, data in data_in.items():
    data_out[row] = data

    if data['issn'] not in vivo_journals:
        # name is not vivo.  These are the ones to add
        data_out[row]['uri'] = ''
    else:
        data_out[row]['uri'] = vivo_journals[data['issn']]

print_err("New journals to add: {}".format(len(data_out)))
write_csv_fp(sys.stdout, data_out)
