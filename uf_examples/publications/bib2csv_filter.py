#!/usr/bin/env/python

"""
    bib2csv_filter.py -- convert bibtex to csv
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys
from bibtexparser import loads
from vivopump import write_csv_fp


def bib2csv(bib_data):
    """
    Given bib_data as created by bibtexparser, return a csv object as modeled by vivotools
    :param bib_data:
    :return: csv_data
    """
    csv_data = {}
    row = 0
    col_names = set(y for x in bib_data.entries for y in x.keys())
    for x in bib_data.entries:
        row += 1
        csv_data[row] = {}
        for col_name in col_names:
            v = x.get(col_name, '')
            v = v.replace('\n', ' ')
            v = v.replace('\r', ' ')
            v = v.replace('\t', ' ')
            csv_data[row][col_name] = v
    return csv_data

bib_str = ""
for line in sys.stdin:
    bib_str += line

bib_data = loads(bib_str)
print >>sys.stderr, "Entries", len(bib_data.entries)
csv_data = bib2csv(bib_data)
print >>sys.stderr, "Rows", len(csv_data)
write_csv_fp(sys.stdout, csv_data)