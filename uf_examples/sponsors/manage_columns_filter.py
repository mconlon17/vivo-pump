#!/usr/bin/env/python

"""
    manage_columns_filter.py -- add needed columns, remove unused columns
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys

from datetime import date

from pump.vivopump import read_csv_fp, write_csv_fp, improve_org_name
from pump.pump import __version__

data_in = read_csv_fp(sys.stdin)
var_names = data_in[data_in.keys()[0]].keys()  # create a list of var_names from the first row
print >>sys.stderr, "Columns in", var_names
data_out = {}
for row, data in data_in.items():
    new_data =dict(data)

    # Add these columns

    new_data['uri'] = ''
    new_data['remove'] = ''
    new_data['funder'] = '1'
    new_data['name'] = improve_org_name(new_data['SponsorName'])
    new_data['sponsorid'] = new_data['Sponsor_ID']
    new_data['date_harvested'] = str(date.today())
    new_data['harvested_by'] = 'VIVO Pump' + ' ' + __version__

    # Delete all the upper case column names

    for name in new_data.keys():
        if name[0] == name[0].upper():
            del new_data[name]

    data_out[row] = new_data
var_names = data_out[data_out.keys()[0]].keys()  # create a list of var_names from the first row
print >>sys.stderr, "Columns out", var_names
write_csv_fp(sys.stdout, data_out)





