#!/usr/bin/env/python

"""
    author_match_filter.py -- find the authors in VIVO, and match them to authors
    in the source.  This is often called disambiguation.

    There are two inputs:
    1. authors in VIVO. Keyed by name parts
    1. authors in the source.  Keyed by name parts

    There are two cases:

    1.  The source indicates the author is not a UF author.  In this case, the author will automatically be added as
    a "stub."  No attempt is made to match stubs.  This leads to proliferation of stubs but is consistent with
    "Assert what you know" and avoids assuming two stubs are the same.
    1.  The source indicates the author is at UF.  In this case, extensive disambiguation matching occurs, based on
    name and name parts.  If no match occurs, the author will be added as a UFEntity.  If multiple matches occur,
    one is selected at random and a disambiguation report entry is produced showing all the possible matches and
    the one that was selected.  Many disambiguation cases involve two URI.  Randomly selecting one cuts the effort to
    assign these potentially by half.  If exactly one match occurs, the match is made, the URI provided in the
    update data.

    See CHANGELOG.md for history
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, get_vivo_authors
import sys


def disambiguate_author(author, vivo_authors=get_vivo_authors()):
    """
    Given an author dictionary with name parts, find matches in the data structure returned by get_vivo_authors
    :param author: dictionary of name parts
    :param vivo_authors: authors in VIVO, seven dictionaries with seven keys based on various types of name parts
    :return: list of uri in vivo matching the author
    """
    author_uri_list = []
    return author_uri_list

data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)
# vivo_authors = get_vivo_authors()  # get dictionaries of authors keyed by name parts
# print >>sys.stderr, 'VIVO authors', len(vivo_authors)
# print >>sys.stderr, vivo_authors
# data_out = {}
# row_out = 0
#
# for row, data in data_in.items():
#     if data['uf'] == 'false':    # Always put in the non-UF author as new
#         row_out += 1
#         data_out[row_out] = data
#         data_out[row_out]['uri'] = ''
#     else:
#         author_uris = disambiguate_author(data, vivo_authors)
#         if len(author_uris) == 0:    # Only put in a new UF author if no one at UF matches
#             row_out += 1
#             data_out[row_out] = data
#             data_out[row_out]['uri'] = ''
#
# print >>sys.stderr, 'data out', len(data_out)
# write_csv_fp(sys.stdout, data_out)





