#!/usr/bin/env/python

"""
    create_shelves.py: Create shelves for person ingest.  Any existing
    shelves are removed and recreated.
    
    Version 0.1 MC 2014-07-19
     -- first version
    Version 0.2 MC 2014-07-20
    --  Six Shelves
    Version 0.3 MC 2015-05-09
    --  For use as a pump example
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "0.3"

import shelve
import os

from datetime import datetime

from pump.vivopump import read_csv


#   Start here

print datetime.now(), "Start"

# Contact

contact_data = read_csv('contact_data.txt')
try:
    os.remove('contact')
except OSError:
    pass
contact = shelve.open('contact')
k = 0
for row, val in contact_data.items():
    k += 1
    if k % 1000 == 0:
        print k
    contact[str(val['UFID'])] = val
print datetime.now(), 'Contact has ', len(contact), 'entries'
contact.close()

# Deptid_exceptions

deptid_exceptions_data = read_csv('deptid_exceptions_data.txt')
try:
    os.remove('deptid_exceptions')
except OSError:
    pass
deptid_exceptions = shelve.open('deptid_exceptions')
k = 0
for row, val in deptid_exceptions_data.items():
    k += 1
    if k % 1000 == 0:
        print k
    deptid_exceptions[str(val['deptid_pattern'])] = val
print datetime.now(), 'Deptid_exceptions has ', len(deptid_exceptions), 'entries'
deptid_exceptions.close()

# ufid_exceptions

ufid_exceptions_data = read_csv('ufid_exceptions_data.txt')
try:
    os.remove('ufid_exceptions')
except OSError:
    pass
ufid_exceptions = shelve.open('ufid_exceptions')
k = 0
for row, val in ufid_exceptions_data.items():
    k += 1
    if k % 1000 == 0:
        print k
    ufid_exceptions[str(val['ufid'])] = val
print datetime.now(), 'Ufid_exceptions has ', len(ufid_exceptions), \
    'entries'
ufid_exceptions.close()

# uri_exceptions

uri_exceptions_data = read_csv('uri_exceptions_data.txt')
try:
    os.remove('uri_exceptions')
except OSError:
    pass
uri_exceptions = shelve.open('uri_exceptions')
k = 0
for row, val in uri_exceptions_data.items():
    k += 1
    if k % 1000 == 0:
        print k
    uri_exceptions[str(val['uri'])] = val
print datetime.now(), 'uri_exceptions has ', len(uri_exceptions), \
    'entries'
uri_exceptions.close()

# position_exceptions

position_exceptions_data = read_csv('position_exceptions_data.txt')
try:
    os.remove('position_exceptions')
except OSError:
    pass
position_exceptions = shelve.open('position_exceptions')
k = 0
for row, val in position_exceptions_data.items():
    k += 1
    if k % 1000 == 0:
        print k
    position_exceptions[str(val['position_title'])] = val
print datetime.now(), 'position_exceptions has ', len(position_exceptions), \
    'entries'
position_exceptions.close()

# Privacy

privacy_data = read_csv('privacy_data.txt')
try:
    os.remove('privacy')
except OSError:
    pass
privacy = shelve.open('privacy')
k = 0
for row, val in privacy_data.items():
    k += 1
    if k % 1000 == 0:
        print k
    privacy[str(val['UFID'])] = val
print datetime.now(), 'Privacy has ', len(privacy), 'entries'
privacy.close()

print datetime.now(), "End"
