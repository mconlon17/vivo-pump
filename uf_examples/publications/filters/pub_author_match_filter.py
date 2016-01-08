#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author_match_filter.py -- find the authors in VIVO, and match them to authors
    in the source.  This is used to match the pubs to an author.

There are two inputs:
    - authors in VIVO keyed by name parts.
    - authors in the source keyed by name parts.

There are two cases:

1.  The source indicates the author is not a UF author.  In this case, the
    author will automatically be added as a "stub."
    No attempt is made to match stubs.  This leads to proliferation of stubs
    but is consistent with "Assert what you know" and avoids assuming two stubs
    are the same.
2.  The source indicates the author is at UF.  In this case, extensive
    disambiguation matching occurs, based on name and name parts.  If no match
    occurs, the author will be added as a UFEntity.  If multiple matches occur,
    one is selected at random and a disambiguation report entry is produced
    showing all the possible matches and the one that was selected.  Many
    disambiguation cases involve two URI.  Randomly selecting one cuts the
    effort to assign these potentially by half.  If exactly one match occurs,
    the match is made, the URI provided in the update data.

"""

__author__ = "Alex Loiacono and Nicholas Rejack"
__copyright__ = "Copyright 2015 (c) Alex Loiacono and Nicholas Rejack"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, get_parms, get_vivo_journals
import utils
import sys

def get_author_name_parts(author_data, max_list_length=50):

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

    utils.print_err("{} Authors in list: {}".format(len(author_list), author_list))
    return author_list

def get_author_uris(author_row_data):

    author_list_out = []

    author_data = get_author_name_parts(author_row_data)

    #utils.print_err("Author data is:\n {}".format(author_data))

    for author in author_data:

        utils.print_err("author is: \n{}".format(author))

        author_uris = utils.get_author_disambiguation_data(
                vivo_auth_disambig_data,
                author['last'],
                author['first'],
                author['middle'])

        #utils.print_err("author_uris: \n{}".format(author_uris))

        count = len(author_uris)

        if count == 1:
            author_list_builder = author_uris[0]
        else:
            author_list_builder = ''
            utils.print_err("Disamb: {}".format(author_uris))

        if len(author_list_out) == 0:
            author_list_out = author_list_builder
            utils.print_err("author_list_out: \n{}".format(author_list_out))
        elif len(author_list_out) >=1 and len(author_list_builder) >0:
            author_list_out += ";"
            author_list_out += author_list_builder

    return author_list_out

def get_author_affiliation(affiliation_row_data):

    from vivopump import replace_initials

    affiliation_list_out = []

    affiliation_parts = affiliation_row_data.split('. ')

    utils.print_err("affiliation_parts = \n{}".format(affiliation_parts))

    for affiliation in affiliation_parts:

        utils.print_err("affiliation = \n{}".format(affiliation))

        if '(Reprint Author)' in affiliation:
            utils.print_err("\nReprint Author found \n")
            if len(affiliation_list_out) > 0:
                affiliation_list_out += ';true'
            else:
                utils.print_err("\naffiliation_list_out < 0\n")
                affiliation_list_out = 'true'
        else:
            if len(affiliation_list_out) > 0:
                affiliation_list_out += ';false'
            else:
                affiliation_list_out = 'false'

    return affiliation_list_out

parms = get_parms()

# Piped in file
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)

# file_name = '/Users/asura/git/vivo-pump/author_list.csv'
# @TODO: pass file name path as a command line parameter
file_name = 'vivo_author_list.csv'
utils.print_err("Using static disambiguation file: {}".format(file_name))

vivo_journals = get_vivo_journals(parms)

# get dictionaries of authors keyed by name parts
vivo_auth_disambig_data = utils.get_vivo_disambiguation_data_from_csv(
    file_name)

utils.print_err("Finished loading {} entries from: {}"
                .format(len(vivo_auth_disambig_data), file_name))
data_out = {}
row_out = 0

for row_index, row_data in data_in.items():
    utils.print_err("\nrow_index is: \n{}".format(row_index))

    utils.print_err("\nrow_data is: \n{}".format(row_data))

    data_out['author'] = get_author_uris(row_data['author'])
    data_out['affiliation'] = get_author_affiliation(row_data['affiliation'])

    try:
        if len(vivo_journals.get(row_data['issn'])) > 0:
            issn_uri = vivo_journals.get(row_data['issn'])
        else:
            utils.print_err("\nISSN not found: {}\n".format(row_data['issn']))
            issn_uri = ''
    except TypeError:
        continue

    # try:
    #     issn_uri = vivo_journals.get(row_data['issn'])
    # except KeyError:
    #     utils.print_err("\nISSN not found: {}\n".format(row_data['issn']))
    #     issn_uri = ''

    utils.print_err("data_out is: \n{}".format(data_out))

    data_in[row_index]['author'] = data_out['author']
    data_in[row_index]['affiliation'] = data_out['affiliation']
    data_in[row_index]['journal'] = issn_uri
    data_in[row_index].pop('issn')

write_csv_fp(sys.stdout, data_in)