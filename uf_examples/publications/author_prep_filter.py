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


def parse_author_data(author_data, affiliation_data, max_list_length=50):
    """
    Parse the author string from TR bibtex.  It has the names of each author.  For each author, determine from
    the affiliation string if the author is the corresponding author (true or false) and if they are a UF author
    (true or false).  Return six data elements for each author -- display_name, last, first, middle names and
    the two true/false values.  Return a list of authors.  Each author has the six elements
    :param author_data:
    :param affiliation_data:
    :param max_list_length: Author list maximum length.  To prevent Physics papers from swamping the process
    :return: author_list.  A list of authors.  Each author is a dict with seven elements.
    """
    author_list = []
    author_names = author_data.split(' and ')
    list_length = 0
    for display_name in author_names:
        list_length += 1
        if list_length > max_list_length:
            break
        display_name = display_name.replace(' -', ' ')  # occasional leading '-' before some initials
        author_dict = {'display_name': display_name, 'suffix': '', 'corresponding': 'false', 'uf': 'false'}
        if ' Jr.,' in display_name:
            author_dict['suffix'] = 'Jr.'
            display_name = display_name.replace(' Jr.,', '')
        if ' III,' in display_name:
            author_dict['suffix'] = 'III'
            display_name = display_name.replace(' III,', '')
        if ',' in display_name:
            k = display_name.find(',')
            author_dict['last'] = display_name[0:k]
            remainder = display_name[k + 2:]
            if ' ' in remainder:
                k = remainder.find(' ')
                author_dict['first'] = remainder[0:k].replace('.', '')
                if ' ' in remainder:
                    k = remainder.find(' ')
                    author_dict['first'] = remainder[0:k].replace('.', '')
                    author_dict['middle'] = remainder[k + 1:].replace('.', '')
            else:
                author_dict['first'] = remainder.replace('.', '')
                author_dict['middle'] = ''
        else:
            author_dict['last'] = display_name
            author_dict['first'] = ''
            author_dict['middle'] = ''
        author_list.append(author_dict)

    # If there is only one author, they must be UF and Corresponding

    if len(author_list) == 1:
        author_list[0]['corresponding'] = 'true'
        author_list[0]['uf'] = 'true'
        return author_list

    # Now find the Corresponding Author

    k = affiliation_data.find('(Reprint Author)')
    if k > 0:
        reprint_name = affiliation_data[0:k - 1]
        k = reprint_name.find(' ')
        reprint_last = reprint_name[0:k - 1]
        reprint_fi = reprint_name[k + 1:k + 2]
        for author_dict in author_list:
            if author_dict['last'] == reprint_last and author_dict['first'][0] == reprint_fi:
                author_dict['corresponding'] = 'true'

    # Now find the UF authors.  Could there be a more arcane format for the affiliations (bunched, etc, etc)

    return author_list

data_in = read_csv_fp(sys.stdin)
var_names = data_in[data_in.keys()[1]].keys()  # create a list of var_names from the first row
print >>sys.stderr, "Columns in", var_names
data_out = {}
row_out = 0
keep_names = set(['remove', 'uri', 'title', 'display_name', 'suffix', 'first', 'last', 'middle', 'corresponding', 'uf'])
for row, data in data_in.items():
    new_data =dict(data)

    author_data = parse_author_data(new_data['author'], new_data['affiliation'])

    # Add these columns

    new_data['remove'] = ''
    new_data['uri'] = ''
    new_data['title'] = key_string(new_data['title'])
    new_data['display_name'] = ''
    new_data['first'] = ''
    new_data['last'] = ''
    new_data['middle'] = ''
    new_data['suffix'] = ''
    new_data['corresponding'] = ''
    new_data['uf'] = ''

    # Delete everything not in the keep_names set

    for name in new_data.keys():
        if name not in keep_names:
            del new_data[name]

    for author in author_data:
        row_out += 1
        data_out[row_out] = dict(new_data)
        for key in author.keys():
            data_out[row_out][key] = author[key]
var_names = data_out[data_out.keys()[1]].keys()  # create a list of var_names from the first row
print >>sys.stderr, "Columns out", var_names
write_csv_fp(sys.stdout, data_out)





