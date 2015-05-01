#!/usr/bin/env/python

"""
    make_person_update_data.py: make the person data for a pump update

    At UF, updating people means updating their contact information and current status with the university. A
    separate process updates positions.

    There are three inputs:
    1. UF people in VIVO, keyed by UFID
    1. UF people on the pay list.  Keyed by UFID
    1. UF People in the contact data.  Keyed by UFID.  Contact data is treated as an attribute source.  If a person
       can not be found in the contact data, the person can not be added to VIVO

    UF business rules apply for adding people to VIVO.  These are enforced in this module.

    Here's an action table based on presence or absence in each of the three sources

    Case VIVO Pay  Con
     7    1    1    1   Current person in VIVO.  Update contact data
     6    1    1    0   Report error.  People must have contact data
     5    1    0    1   Not current person.  Update contact
     4    1    0    0   Report error.  People must have contact data
     3    0    1    1   New Current person.  Add to VIVO.  Update contact data
     2    0    1    0   Report error.  People must have contact data
     1    0    0    1   Nothing to do
     0    0    0    0   Nothing to do

    See CHANGELOG.md for history

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.02"

from vivopump import vivo_query, read_csv


def report_error(s):
    """
    Given an error report string s, print to appropriate location
    :param s: error report
    :return: None
    """
    print s
    return None


def get_vivo_ufid():
    """
    Query VIVO and return a list of all the ufid found in VIVO
    :return: list of UFID in VIVO
    """
    query = "select ?uri ?ufid where {?uri uf:ufid ?ufid .}"
    a = vivo_query(query)
    return [x['ufid']['value'] for x in a['results']['bindings']]


def get_pay_ufid(filename, delimiter='|'):
    """
    Read the current position data and return a list of all the UFID found in it
    :param filename: name of file containing position data
    :param delimiter: delimiter used in the position data file
    :return: list of UFID in position data
    """
    vivo_plans = ()
    pay_data = read_csv(filename, delimiter=delimiter)
    return [pay_data[x]['UFID'] for x in pay_data if pay_data[x]['SAL_ADMIN_PLAN'] in vivo_plans]


def get_dir_ufid():
    l = []
    return l


def get_dir_data():
    data = []
    return data

# get data from each of the three sources

vivo_ufid = get_vivo_ufid()  # includes UF people with ufid
pay_ufid = get_pay_ufid()  # includes only those who qualify for VIVO
dir_ufid = get_dir_ufid()  # includes all people with ufid and contact data (big)
dir_data = get_dir_data()  # includes all contact data for UF (very, very big)

for ufid in vivo_ufid + pay_ufid:
    case = 7
    if ufid not in vivo_ufid:
        case -= 4
    if ufid not in pay_ufid:
        case -= 2
    if ufid not in dir_ufid:
        case -= 1

    if case == 7:
        # Existing current person, update contact
        row = dir_data[ufid]
        row['current'] = True
    elif case == 6:
        # report error
        report_error('No contact data for ' + ufid)
    elif case == 5:
        # not current, update contact
        row = dir_data[ufid]
        row['current'] = False
    elif case == 4:
        # report error
        report_error('No contact data for ' + ufid)
    elif case == 3:
        # New current person.  Add to VIVO
        row = dir_data[ufid]
        row['current'] = True
    elif case == 2:
        # report error.
        report_error('No contact data for ' + ufid)
    else:
        pass





