#!/usr/bin/env/python

"""
    create_shelves.py: Create shelves for person ingest.  Any existing
    shelves are removed and recreated.
    
    Version 0.1 MC 2014-07-19
     -- first version
    Version 0.2 MC 2014-07-20
    --  Six Shelves
    Version 0.3 MC 2015-05-04
    -- For use with the pump
"""

# TODO: Consider processing all the exceptions

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "0.3"

from datetime import datetime
from vivopump import read_csv
import shelve
import os

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

print datetime.now(), "End"
