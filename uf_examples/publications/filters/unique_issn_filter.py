#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
unique_issn_filter.py -- remove duplicate issn
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp

data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, "Input rows", len(data_in)

data_out = {}
issn_out = set()

for row, data in data_in.items():
    new_data = dict(data)
    if data['issn'] not in issn_out:
        data_out[row] = new_data
        issn_out.add(data['issn'])
print >>sys.stderr, "Output rows", len(data_out)
write_csv_fp(sys.stdout, data_out)
