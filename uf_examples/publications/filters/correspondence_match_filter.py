#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author_correspondence_match_filter.py -- find the authorships in VIVO and based
    on the input file assign whether or not a particular author is the
    corresponding author on a paper

There are two inputs:
    - authorships in VIVO keyed by name parts.
    - authors in the source keyed by name parts.

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

    utils.print_err("authorship_dict is: \n{}".format(authorship_dict))

for row_index, row_data in data_in.items():

    utils.print_err("row_data[row_index]: \n{}".format(row_data))

    data_out['authorship_uri'] = authorship_dict[row_data['display_name']][row_data['title']]
    data_out['corresponding'] = row_data['corresponding']

    utils.print_err("authorhip uri: \n{}".format(data_out.keys()))

with open('correspondence.txt', 'w') as fp:
    a = csv.DictWriter(fp, delimiter='|',fieldnames=data_out.keys())
    a.writeheader()
    for row in data_out:
        a.writerow(row)