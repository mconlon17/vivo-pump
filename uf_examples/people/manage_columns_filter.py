#!/usr/bin/env/python

"""
    manage_columns_filter.py -- add needed columns, remove unused columns
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp

data_in = read_csv_fp(sys.stdin)
var_names = data_in[data_in.keys()[0]].keys()  # create a list of var_names from the first row
print >>sys.stderr, "Columns in", var_names
data_out = {}
for row, data in data_in.items():
    new_data =dict(data)

    # Delete these columns

    del new_data['JOBCODE']
    del new_data['HR_POSITION']
    del new_data['DEPTID']
    del new_data['SAL_ADMIN_PLAN']
    del new_data['START_DATE']
    del new_data['END_DATE']
    del new_data['JOBCODE_DESCRIPTION']

    # Add these columns

    new_data['remove'] = ''
    new_data['uri'] = ''
    new_data['current'] = ''
    data_out[row] = new_data
var_names = data_out[data_out.keys()[0]].keys()  # create a list of var_names from the first row
print >>sys.stderr, "Columns out", var_names
write_csv_fp(sys.stdout, data_out)





