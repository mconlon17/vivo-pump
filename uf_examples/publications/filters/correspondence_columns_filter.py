#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    author_prep_filter.py -- add needed columns, remove unused columns.  This
    filter is more sophisticated than most:

    It handles the affiliation parsing, identifying corresponding author and UF
    authors. It transposes the data from publication records to author records.
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
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

from utils import print_err
from vivopump import read_csv_fp, write_csv_fp, improve_display_name, improve_title
import sys


def parse_author_data(author_data, affiliation_data, max_list_length=50):
    """
    Parse the author string from TR bibtex.  It has the names of each author.
    For each author, determine from the affiliation string if the author is the
    corresponding author (true or false) and if they are a UF author (true or
    false).  Return six data elements for each author -- display_name, last,
    first, middle names and the two true/false values.  Return a list of
    authors.  Each author has the six elements :param author_data: :param
    affiliation_data:

    :param max_list_length: Author list maximum length.  To prevent Physics
        papers from swamping the process
    :return: author_list.  A list of authors. Each author is a dict with seven
    elements.
    """
    from vivopump import replace_initials
    author_list = []
    author_names = author_data.split(' and ')
    list_length = 0

    for display_name in author_names:
        list_length += 1
        if list_length > max_list_length:
            break

        # occasional leading '-' before some initials
        display_name = display_name.replace(' -', ' ')
        author_dict = {'display_name': display_name,
                       'suffix': '',
                       'corresponding': 'false',
                       'uf': 'false'}

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
            if author_dict['last'] == reprint_last \
                    and author_dict['first'][0] == reprint_fi:
                author_dict['corresponding'] = 'true'

    # Now find the UF authors.  Could there be a more arcane format for the
    # affiliations (bunched, etc, etc), So first thing we do is build a
    # structure that can identify who is a UF author

    # periods are used for ending initials in names. Remove these
    affiliation_data = replace_initials(affiliation_data)

    # Now periods demarc the groups of authors with like affiliation
    affiliation_list = affiliation_data.split('.')
    affiliations = []

    for affiliation_string in affiliation_list:
        affiliation = {'affiliation_string': affiliation_string}
        if 'Univ Florida' in affiliation_string:
            affiliation['uf'] = 'true'
        else:
            affiliation['uf'] = 'false'
    affiliations.append(affiliation)
    print_err(affiliations)

    # Now we are ready to look for affiliations by name.  Messy business.
    for author_dict in author_list:
        if author_dict['first'] == '':
            # corporate authors can not be UF authors
            continue
        find_string = author_dict['last'] + ', ' + author_dict['first'][0]

        for affiliation in affiliations:  # look in each affiliation group
            if affiliation['affiliation_string'].find(find_string) > -1:
                author_dict['uf'] = affiliation['uf']
                # if you find the author, use the affiliation of the group
                # and don't look further.  If you don't find the author
                # the default affiliation is uf false
                continue

    print_err("{} Authors in list: {}".format(len(author_list), author_list))
    return author_list

data_in = read_csv_fp(sys.stdin)

column_names = data_in[1].keys()
print_err("==> {} columns in the input: {} "
          .format(len(column_names), column_names))

data_out = {}
row_out = 0
keep_names = set(['remove', 'display_name','corresponding', 'title'])

for row, data in data_in.items():
    new_data = dict(data)
    author_data = parse_author_data(new_data['author'],
                                    new_data['affiliation'])

    # Add these columns
    new_data['remove'] = ''
    new_data['display_name'] = ''
    new_data['corresponding'] = ''
    new_data['title'] = improve_title(new_data['title'])

    # Delete everything not in the keep_names set
    for name in new_data.keys():
        if name not in keep_names:
            del new_data[name]

    for author in author_data:
        row_out += 1
        data_out[row_out] = dict(new_data)
        for key in author.keys():
            data_out[row_out][key] = author[key]

            if key == 'display_name':
                data_out[row_out][key] = improve_display_name(author[key])

column_names_out = data_out[1].keys()
print_err("==> {} columns in the output: {}"
          .format(len(column_names_out), column_names_out))
write_csv_fp(sys.stdout, data_out)
