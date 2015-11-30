#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
publisher_columns_filter.py -- add needed columns, remove unused columns
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, improve_org_name
import sys

data_in = read_csv_fp(sys.stdin)
# create a list of var_names from the first row
var_names = data_in[data_in.keys()[1]].keys()
print >>sys.stderr, "Columns in", var_names

data_out = {}
keep_names = set(['remove', 'uri', 'name', 'type'])

for row, data in data_in.items():
    new_data = dict(data)

    # Add these columns
    new_data['remove'] = ''
    new_data['uri'] = ''
    new_data['name'] = improve_org_name(new_data['publisher']).upper()
    new_data['type'] = 'publisher'

    # Delete everything not in the keep_names set
    for name in new_data.keys():
        if name not in keep_names:
            del new_data[name]

    data_out[row] = new_data

# create a list of var_names from the first row
var_names = data_out[data_out.keys()[1]].keys()
print >>sys.stderr, "Columns out", var_names
write_csv_fp(sys.stdout, data_out)
