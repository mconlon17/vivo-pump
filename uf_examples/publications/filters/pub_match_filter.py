#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pub_match_filter.py -- find the academic articles in VIVO, and match them by
    the doi to the pubs in the source.

There are two inputs:
    1. pubs in VIVO keyed by doi
    2. pubs in the source keyed by doi

There are three cases
    - pub in VIVO and in source => add to update data with uri
    - pub in VIVO, not in source => nothing to do
    - pub not in VIVO, is in source => Add to update data with blank uri
    (to be assigned during update)
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys

from pump.vivopump import read_csv_fp, write_csv_fp, get_parms, vivo_query
from disambiguate.utils import print_err


def get_vivo_academic_articles(parms):
    """
    Query VIVO and return a list of all the academic articles.
    @see uf_examples/publications/filters/pub_match_filter.py
    @see https://wiki.duraspace.org/display/VIVO/VIVO-ISF+1.6+relationship+diagrams%3A+Authorship

    :param: parms: vivo_query params
    :return: dictionary of uri keyed by DOI
    """
    query = """
    SELECT
    ?uri ?doi
    WHERE {
        ?uri a vivo:InformationResource .
        ?uri bibo:doi ?doi .
    }
    """
    results = vivo_query(query, parms)
    bindings = results['results']['bindings']
    doi_list = [b['doi']['value'] for b in bindings]
    uri_list = [b['uri']['value'] for b in bindings]
    return dict(zip(doi_list, uri_list))

parms = get_parms()
data_in = read_csv_fp(sys.stdin)
print_err("{} rows in the input".format(len(data_in)))

data_out = {}
# get dictionary of pub uri keyed by doi
vivo_pubs = get_vivo_academic_articles(parms)

print_err('{} publications found in VIVO'.format(len(vivo_pubs)))
# print >>sys.stderr, vivo_pubs

for row, data in data_in.items():
    data_out[row] = data

    # name is not vivo.  These are the ones to add
    if data['doi'] not in vivo_pubs:
        data_out[row]['uri'] = ''
    else:
        data_out[row]['uri'] = vivo_pubs[data['doi']]

print_err('{} rows in the output'.format(len(data_out)))
write_csv_fp(sys.stdout, data_out)
