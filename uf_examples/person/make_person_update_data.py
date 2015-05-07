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

from vivopump import vivo_query, read_csv, write_csv
import shelve



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


def get_pay_ufid(filename, plan_name, delimiter='|'):
    """
    Read the current position data and return a list of all the UFID found in it
        with qualifying pay plans
        exclude lump sum payments

    :param filename: name of file containing position data
    :param delimiter: delimiter used in the position data file
    :return: list of UFID in position data
    """
    plan_data = read_csv(plan_name, delimiter='\t')
    vivo_plans = [plan_data[x]['short'] for x in plan_data if plan_data[x]['vivo'] != "None"]
    print vivo_plans
    pay_data = read_csv(filename, delimiter=delimiter)
    print len(pay_data)
    return [pay_data[x]['UFID'] for x in pay_data if pay_data[x]['SAL_ADMIN_PLAN'] in vivo_plans and
            pay_data[x]['JOBCODE_DESCRIPTION'] != 'ACADEMIC LUMP SUM PAYMENT']


# Main Starts here
#
# get data from each of the three sources

contact = shelve.open('contact.db')
print "Contact data has ", len(contact), "entries"
ufid = "84808900"
if ufid in contact.keys():
    print contact[ufid]
vivo_ufid = get_vivo_ufid()  # includes UF people with ufid
print "VIVO UFID", vivo_ufid
pay_ufid = get_pay_ufid('position_data.csv',
                        'salary_plan_enum.txt')  # includes only those who qualify for VIVO
print "PAY UFID", len(pay_ufid)

row_number = 0  # For output, count the umber of rows in the resulting update csv
all_row = 0
person_update_data = {}
contact_keys = contact.keys()

for ufid in vivo_ufid + pay_ufid:
    all_row += 1
    row = {}
    case = 7
    if ufid not in vivo_ufid:
        case -= 4
    if ufid not in pay_ufid:
        case -= 2
    if ufid not in contact_keys:
        case -= 1

    if case == 7:
        # Existing current person, update contact
        row = contact[ufid]
        row['current'] = "yes"
    elif case == 6:
        # report error
        report_error('Person in VIVO and pay list.  No contact data for ' + ufid)
    elif case == 5:
        # not current, update contact
        row = contact[ufid]
        row['current'] = "no"
    elif case == 4:
        # report error
        report_error('Person in VIVO.  No contact data ' + ufid)
    elif case == 3:
        # New current person.  Add to VIVO
        row = contact[ufid]
        row['current'] = "yes"
    elif case == 2:
        # report error.
        # report_error('Person on pay list.  No contact data for ' + ufid)
        pass
    else:
        pass
    if row != {}:
        row_number += 1
        person_update_data[row_number] = row
    if all_row % 100 == 0:
        print all_row, row_number, case, row
write_csv('uf_person_data.txt', person_update_data, delimiter='\t')
contact.close()





