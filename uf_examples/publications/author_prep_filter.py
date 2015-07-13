#!/usr/bin/env/python

"""
    author_prep_filter.py -- add needed columns, remove unused columns.  This filter is more sophisticated
    than most:

    It handles the affiliation parsing, identifying corresponding author and UF authors.
    It transposes the data from publication records to author records.
    It handles the disambiguation of UF authors.

    Input

    title1  affil string 1  author names string 1
    title2  affil string 2  author names string 2

    Output

    title1  author1 corresponding1  uf1
    title1  author2 corresponding2  uf2
    title1  author3 corresponding3  uf3
    title2  author1 corresponding1  uf1 (author 1 of the second paper)
    title2  author2 corresponding2  uf2

    etc.

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, key_string
import sys

data_in = read_csv_fp(sys.stdin)
var_names = data_in[data_in.keys()[1]].keys()  # create a list of var_names from the first row
print >>sys.stderr, "Columns in", var_names
data_out = {}
keep_names = set(['remove', 'uri', 'title', 'display_name', 'first', 'last', 'middle', 'corresponding', 'uf'])
for row, data in data_in.items():
    new_data =dict(data)

    # Add these columns

    new_data['remove'] = ''
    new_data['uri'] = ''
    new_data['title'] = key_string(new_data['title'])
    new_data['display_name'] = ''
    new_data['first'] = ''
    new_data['last'] = ''
    new_data['middle'] = ''
    new_data['corresponding'] = ''
    new_data['uf'] = ''

    # Delete everything not in the keep_names set

    for name in new_data.keys():
        if name not in keep_names:
            del new_data[name]

    data_out[row] = new_data
var_names = data_out[data_out.keys()[1]].keys()  # create a list of var_names from the first row
print >>sys.stderr, "Columns out", var_names
write_csv_fp(sys.stdout, data_out)





