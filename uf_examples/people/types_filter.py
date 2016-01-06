#!/usr/bin/env/python

"""
    types_filter.py -- Create a types value for managing people types.  This is a bit of nasty business.  Person
    types consists of different kinds of information, all rolled in to a "types" field that is multi-valued. The
    source data is authoritative for two concepts -- the type of the current position, which UF maps to the type of
    the person.  So for example, if a person has a Faculty position, they are assumed to be a people member.  But
    there is no way for this filter to remove types that might now be obsolete -- the source data contains only
    the current position type.  Other type information comes from other authoritative sources and in some
    cases is managed within VIVO (VIVOOptIn, for example).  The source is also authoritative for current status.
    If the person is in the position data, they are current, if not, they are not current.

    In processing of data for UF people, a previous filter (merge_filter) determines whether the person was
    in the source and/or VIVO and set the value of the 'current' column to 'yes' if the person is current and 'no'
    otherwise.
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c), Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp, get_vivo_types, get_parms, read_csv

parms = get_parms()
type_data = read_csv('person_types.txt', delimiter='\t')
type_enum = {type_data[row]['vivo']: type_data[row]['short'] for row in type_data}  # convert spreadsheet to dict
plan_data = read_csv('salary_plan_enum.txt', delimiter='\t')
plan_enum = {plan_data[row]['short']: plan_data[row]['vivo'] for row in plan_data}  # convert spreadsheet to dict
vivo_types = get_vivo_types("?uri a uf:UFEntity . ?uri a foaf:Person .", parms)  # must match entity_sparql
data_in = read_csv_fp(sys.stdin)
data_out = {}
for row, data in data_in.items():
    new_data =dict(data)

    #   Convert the source type to a VIVO type.  The source has an HR code.  Convert that to a VIVO person type URI
    #   using the plan_enum.  Then convert that to the value to be stored in the type data.  Whew.

    src_type = new_data['types']
    if src_type in plan_enum:
        src_type = type_enum[plan_enum[src_type]]

    #   Prepare the types column with values from VIVO, if any

    if new_data['uri'] in vivo_types:
        type_list = vivo_types[new_data['uri']].split(';')
        enum_list = []
        for type_uri in type_list:
            if type_uri in type_enum:
                enum_list.append(type_enum[type_uri])
        types = ';'.join(enum_list)
    else:
        types = 'uf'

    if types.find(src_type) < 0:
        types = types + ';' + src_type

    #   Update the "ufc" code in types (UFCurrentEntity) based on the values in the 'current' column

    if new_data['current'] == 'yes' and types.find('ufc') < 0:
        types += ';ufc'
    elif new_data['current'] == 'no' and types.find('ufc') > -1:
        types = types.replace('ufc', '')

    #   All done.  Assign the new types

    new_data['types'] = types
    data_out[row] = new_data
write_csv_fp(sys.stdout, data_out)





