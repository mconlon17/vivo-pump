#!/usr/bin/env/python

"""
    contact_filter.py -- add contact data to the people to be updated
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import shelve
import sys

from pump.vivopump import read_csv_fp, write_csv_fp, improve_phone_number, improve_display_name, \
    improve_jobcode_description

contact_shelve = shelve.open('contact.db')
contact_ufids = set(contact_shelve.keys())  # a set of ufids that will not be in the output
contact_names = set(contact_shelve[contact_ufids.pop()].keys())
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
found = 0
not_found = 0
data_out = {}
for row, data in data_in.items():
    new_data = dict(data)
    if data['UFID'] in contact_ufids:
        found += 1
        contact_data = contact_shelve[data['UFID']]
        for name, value in contact_data.items():
            new_data[name] = value
        new_data['UF_BUSINESS_FAX'] = improve_phone_number(new_data['UF_BUSINESS_FAX'])
        new_data['UF_BUSINESS_PHONE'] = improve_phone_number(new_data['UF_BUSINESS_PHONE'])
        new_data['DISPLAY_NAME'] = improve_display_name(new_data['DISPLAY_NAME'])
        new_data['WORKINGTITLE'] = improve_jobcode_description(new_data['WORKINGTITLE'])
    else:
        not_found += 1
        for name in contact_names:
            new_data[name] = ''
    data_out[row] = new_data
print >>sys.stderr, 'Found', found
print >>sys.stderr, 'Not found', not_found
write_csv_fp(sys.stdout, data_out)
contact_shelve.close()





