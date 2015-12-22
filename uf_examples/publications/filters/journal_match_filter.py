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

from utils import print_err
from vivopump import read_csv_fp, write_csv_fp, get_vivo_journals, get_parms, get_vivo_publishers, improve_org_name, read_csv
import sys
import fileinput

names = read_csv("filters/publisher_name_filter.csv")

def publisher_name_filter(input_publisher):

    new_pub_name = input_publisher

    print_err("input_publisher is: {}".format(input_publisher))
    for row in names.values():
        if input_publisher == row['original']:
            #print_err("We found a match at {}".format(row['original']))
            new_pub_name = row['improved']
            # print_err("improve name is: {}".format(new_pub_name))
            # line = input_publisher.replace(row['original'], row['improved'])
            return new_pub_name

    #print_err("returned_publisher is: {}".format(input_publisher))
    return new_pub_name




parms = get_parms()
data_in = read_csv_fp(sys.stdin)
print_err("Input data length: {}".format(len(data_in)))

data_out = {}


vivo_publishers = get_vivo_publishers(parms)

#print_err("\n\nvivo_publishers: \n{}\n\n".format(vivo_publishers))

# get dictionary of journal uri keyed by
# International Standard Serial Numbers (ISSN)
vivo_journals = get_vivo_journals(parms)
print_err('There are {} journals in VIVO'.format(len(vivo_journals)))
print_err(vivo_publishers)

for row, data in data_in.items():
    data_out[row] = data

    if data['issn'] not in vivo_journals:
        # name is not vivo.  These are the ones to add
        print_err("issn not found in vivo")
        print_err(data_in[row]['publisher'])
        data_out[row]['uri'] = ''
        print_err("vivo_publishers[{}]".format(vivo_publishers[publisher_name_filter(improve_org_name(data_in[row]['publisher']).upper()).lower()\
            .replace(' ','').replace(',','').replace('-','').replace('.','')]))

        data_out[row]['publisher'] = vivo_publishers[publisher_name_filter(improve_org_name(data_in[row]['publisher']).upper()).lower()\
            .replace(' ','').replace(',','').replace('-','').replace('.','').replace('/','')]
        #data_out[row]['publisher'] = vivo_publishers[data_in[row]['publisher'].encode()]


    else:
        print_err("issn found in vivo")
        print_err(data_in[row]['publisher'])
        data_out[row]['uri'] = vivo_journals[data['issn']]
        #data_out[row]['publisher'] = vivo_publishers[data_in[row]['publisher'].lower().replace(' ','').encode()]
        data_out[row]['publisher'] = vivo_publishers[publisher_name_filter(improve_org_name(data_in[row]['publisher']).upper()).lower()\
            .replace(' ','').replace(',','').replace('-','').replace('.','').replace('/','')]

print_err("New journals to add: {}".format(len(data_out)))
write_csv_fp(sys.stdout, data_out)
