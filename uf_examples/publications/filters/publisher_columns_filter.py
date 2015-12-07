#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
publisher_columns_filter.py -- add needed columns, remove unused columns
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

from utils import print_err
from vivopump import read_csv_fp, write_csv_fp, improve_org_name
import sys

data_in = read_csv_fp(sys.stdin)

# The first filter should fail if there is no data to process
assert(len(data_in) > 0)

# import pprint; pprint.pprint(data_in)

# create a list of
column_names = data_in[1].keys()
print_err("==> {} columns in the input: {} "
          .format(len(column_names), column_names))

data_out = {}
keep_names = set(['remove', 'uri', 'name', 'type'])

for row, data in data_in.items():
    if 'publisher' not in data:
        raise Exception("The input row {} is missing the 'publisher' value"
                        .format(row))
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

column_names_out = data_out[1].keys()
print_err("==> {} columns in the output: {}"
          .format(len(column_names_out), column_names_out))
write_csv_fp(sys.stdout, data_out)
