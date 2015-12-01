#!/usr/bin/env python


"""
fix_bibtex.py -- fix a bibtex file

Thomson Reuters Bibtex has several errors that violate bibtex sytax and
choke bibtex parsers.  These are:
    1.  Double brackets should be replaced with single brackets throughout.
        For example, Thomson Reuters often uses Year = {{1988}}.  Should be
        Year = {1988}
    2.  Bibtex keywords must not contain blanks.  Thomson Reuters asserts
        Web of Science Category = {...}  All assertions should be changed to
        Web-of-Science-Category = {...}
        Meeting Abstract should be changed to Meeting-Abstract = {...}
    3.  The values for Funding-Acknowledgement often (about 30% of the time)
        include a meaningless escape sequence \{[}\} which confuses the
        parser.  This string of six characters should be replaced everywhere
        with a single space.

In addition, Thomson Reuters uses a series of abbreviations for journal
names and publishers that can be improved on a case by case basis.

This program reads a file of improvements, and a bibtex file from stdin,
makes the improvements that need to be made, and writes an improved
file to stdout.

Version 1.0 2012-08-25 MC
--  Added additional publisher name corrections
Version 1.1 2014-01-13 MC
--  All data moved to a CSV file
--  Conform with commenting and coding standards
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.1"

import sys
import fileinput
from vivopump import read_csv

names = read_csv("filters/publisher_name_filter.csv")

for line in fileinput.input():
    for row in names.values():
        line = line.replace(row['original'], row['improved'])
    sys.stdout.write(line)
