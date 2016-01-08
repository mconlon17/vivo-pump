#!/usr/bin/env python

"""
author_match_filter.py -- find the authors in VIVO, and match them to authors
    in the source.  This is often called disambiguation.

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

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

from vivopump import read_csv_fp, write_csv_fp, get_parms
import utils
import sys

parms = get_parms()
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, len(data_in)

# file_name = '/Users/asura/git/vivo-pump/author_list.csv'
# @TODO: pass file name path as a command line parameter
file_name = 'vivo_author_list.csv'
utils.print_err("Using static disambiguation file: {}".format(file_name))

# get dictionaries of authors keyed by name parts
vivo_auth_disambig_data = utils.get_vivo_disambiguation_data_from_csv(
    file_name)

utils.print_err("Finished loading {} entries from: {}"
                .format(len(vivo_auth_disambig_data), file_name))
data_out = {}
row_out = 0
new_authors = 0
non_uf = 0

"""
Example of rows in data_in:

display_name        | suffix  | first   | uri | remove| middle| corresponding | uf  | last
Stienmetz, Jason L. |         | Jason   |     |       | L     |  true         | true| Stienmetz
"""

utils.print_err("length of data in {}".format(len(data_in)))


for row_index, row_data in data_in.items():

    if row_data['uf'] == 'false':
        # Always put in the non-UF author as new
        row_out += 1
        non_uf += 1
        data_out[row_out] = row_data
        data_out[row_out]['uri'] = ''
        #utils.print_err("UF entry is false {}".format(row_index))
    else:
        author_uris = utils.get_author_disambiguation_data(
            vivo_auth_disambig_data,
            row_data['last'],
            row_data['first'],
            row_data['middle'])

        count = len(author_uris)
        if count == 0:
            # There is no match in the current VIVO ==> add a new UF author
            row_out += 1
            new_authors += 1
            data_out[row_out] = row_data
            data_out[row_out]['uri'] = ''
            #utils.print_err("uri count 0 for {}".format(row_data))
        # elif count == 1:
        #     # Bingo! Disambiguated UF author. Add URI
        #     #row_out += 1
        #     data_out[row_out] = row_data
        #     utils.print_err("row {} - author_uris: {}"
        #                     .format(row_out, author_uris))
        #     # sys.exit()
        #     data_out[row_out]['uri'] = author_uris[0]
        #     action = "Found UF"
        #     utils.print_err("uri count 1 for {}".format(row_index))
        # else:
        #     # More than one UF author matches. Add to the disambiguation list.
        #     #row_out += 1
        #     data_out[row_out] = row_data
        #     data_out[row_out]['uri'] = ";".join(author_uris)
        #     action = 'Disambig'
        #     utils.print_err("uri count 2 for {}".format(row_index))

# data_out = {}
name_out = set()

#
# for row, data in data_in.items():
#     new_data = dict((data_in_keys,'') for data_in_keys in data)
#     utils.print_err(new_data)
#     if data['display_name'] not in name_out:
#         data_out[row] = new_data
#         name_out.add(data['display_name'])

print >>sys.stderr, 'data out', len(data_out)
print >>sys.stderr, 'non uf authors', non_uf
print >>sys.stderr, 'number of new authors', new_authors
write_csv_fp(sys.stdout, data_out)
