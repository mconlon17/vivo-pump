#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author_correspondence_match_filter.py -- find the authorships in VIVO and based
    on the input file assign whether or not a particular author is the
    corresponding author on a paper

There are two inputs:
    - authorships in VIVO keyed on author name and title of paper.
    - authors in the source keyed by name and title of paper.

Creates a file from vivo of title_of_paper|authorship_uri|author_name

Reads in the same output produced from author_match_filter

Authorship dictionary is then keyed of author_name with a secdondary
    key of the title of the paper. From this we can index the
    authorship dictionary to get the authorship uri and assign
    the correspondence property.

"""

from vivopump import read_csv, write_csv_fp, get_parms, read_csv_fp
import utils
import csv
import sys

parms = get_parms()
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)

data_out = {}

file_name = 'vivo_authorships.csv'

authorship_dict = dict()

with open(file_name, 'rb') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
    count = 0

    for row in reader:
        name = row['authorName']
        try:
            pub_label = row['label']
            authorship_dict[name][pub_label] = row['authorship']
        except:
            authorship_dict[name] = dict()
            pub_label = row['label']
            authorship_dict[name][pub_label] = row['authorship']

    #utils.print_err("authorship_dict is: \n{}".format(authorship_dict))

for row_index, row_data in data_in.items():

    data_out[row_index] = row_data

    data_out[row_index]['uri'] = authorship_dict[row_data['display_name']][row_data['title']]
    data_out[row_index]['corresponding'] = row_data['corresponding']

for key in data_out[1].keys():
    utils.print_err("key:\n{}".format(key))
    if key != 'corresponding' and key != 'uri':
        #utils.print_err("removing key\n")
        data_out[1].pop(key)

write_csv_fp(sys.stdout, data_out)