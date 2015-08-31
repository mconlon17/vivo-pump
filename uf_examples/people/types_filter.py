#!/usr/bin/env/python

"""
    types_filter.py -- Create a types value for managing people types.  This is a bit of nasty business.  Person
    type consists of different kinds of information, all rolled in to a "type" field that is multi-valued. The
    source data is authoritative for two concepts -- the type of the current position, which UF maps to the type of
    the person.  So for example, if a person has a Faculty position, they are assumed to be a faculty member.  The
    source is also authoritative for current status.  If the person is in the position data, they are current.

    In the processing of data for UF people, a previous filter (merge_filter) determined whether the person was
    in the source and/or VIVO and set the value of the 'current' column to 'yes' if the person is current and 'no'
    otherwise.
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c), Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, get_vivo_types
import sys

data_in = read_csv_fp(sys.stdin)
data_out = {}
null_count = 0
for row, data in data_in.items():
    new_data =dict(data)
    vivo_types = get_vivo_types("?uri a uf:UFEntity .")
    data_out[row] = new_data
print >>sys.stderr, "NULL values replaced", null_count
write_csv_fp(sys.stdout, data_out)





