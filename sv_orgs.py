#!/usr/bin/env/python

"""
    sv_orgs.py: Simple VIVO for Organizations

    Read a spreadsheet and follow the directions to add, update or remove organizations and/or
    organization attributes from VIVO.

    Exceptions are thrown, caught and logged for missing required elements that are missing

    See CHANGELOG.md for history

    To Do:
    --  Create a test file with orgs and test case notes
    --  Use rdflib
    --  Use an update design.  Always
    --  Use argparse to handle command line arguments
    --  Support look up by uri or name

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.0"
