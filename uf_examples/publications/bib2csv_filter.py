#!/usr/bin/env/python

"""
    bib2csv_filter.py -- convert bibtex to csv
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015"
__license__ = "New BSD License"
__version__ = "0.01"

import sys
import bibtexparser

bib_str = ""
for line in sys.stdin:
    bib_str += line

bib_data = bibtexparser.loads(bib_str)
print >>sys.stderr, "Entries", len(bib_data.entries)

col_names = set(y for x in bib_data.entries for y in x.keys())
print len(col_names), col_names






