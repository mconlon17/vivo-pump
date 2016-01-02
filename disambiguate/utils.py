# -*- coding: utf-8 -*-
"""
utils.py - helper functions
"""

from __future__ import print_function
from sys import stderr
import csv

from disambiguate.vivo_name import VivoName
from disambiguate.vivo_name import CASE_0, CASE_1, CASE_2, CASE_3, CASE_4, CASE_5, CASE_6

__author__ = "Andrei Sura"
__copyright__ = "Copyright (c) 2016 Andrei Sura"
__license__ = "New BSD license"
__version__ = "0.8.5"


def print_err(*args, **kwargs):
    """
    python3-compatible helper for printing to stderr
    """
    print(*args, file=stderr, **kwargs)


def append_to_dict_list(modified_dict, key, val):
    """
    :return a list with an extra element
        The list is retrieved from the `modified_dict` at address `key`
    """

    try:
        my_list = modified_dict[key]
    except IndexError:
        # there is no list at the specified key therefore init one
        my_list = []
    my_list.append(val)

    # implementation which does not modify the original dictionary
    # my_list = []
    # if key in modified_dict:
    #     # import copy
    #     # my_list = copy.copy(modified_dict[key])
    #     my_list = [x for x in modified_dict[key]]
    # my_list.append(val)
    return my_list


def get_vivo_disambiguation_data_from_csv(file_name):
    """"
    Loop through the specified csv file which contains one vivo person per row
    and generate all possible patterns from the person's name fragments.

    return: {
        'case_0': {
            'name_pattern_a': [uri1, uri2...],
            'name_pattern_b': [uri1, uri2...],
        },
        'case_1': {
            'name_pattern_a': [uri1, uri2...],
            'name_pattern_b': [uri1, uri2...],
        },
        ...
        'case_6': {
            'name_pattern_a': [uri1, uri2...],
            'name_pattern_b': [uri1, uri2...],
        }
    }

    Note: the logic in this file was borrowed from the original implementation
    in bibtex2rdf.py (git@ctsit-forge.ctsi.ufl.edu:vivo-pub-ingest.git)
    """
    case0_dict = {}
    case1_dict = {}
    case2_dict = {}
    case3_dict = {}
    case4_dict = {}
    case5_dict = {}
    case6_dict = {}

    with open(file_name, 'rb') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar=None)
        count = 0

        for row in reader:
            count += 1
            if count == 1:
                # skip the first row
                continue
            uri = row[0].strip()
            fname = row[1].strip()
            lname = row[2].strip()
            mname = row[3].strip()

            vname = VivoName(lname, fname, mname)

            # @TODO: move the logic to the vivo_name
            k0 = vname.get_key_0()
            case0_dict[k0] = append_to_dict_list(case0_dict, k0, uri)

            if vname.has_first():
                k1 = vname.get_key_1()
                k2 = vname.get_key_2()
                case1_dict[k1] = append_to_dict_list(case1_dict, k1, uri)
                case2_dict[k2] = append_to_dict_list(case2_dict, k2, uri)

                if vname.has_middle():
                    k3 = vname.get_key_3()
                    k4 = vname.get_key_4()
                    k5 = vname.get_key_5()
                    k6 = vname.get_key_6()
                    case3_dict[k3] = append_to_dict_list(case3_dict, k3, uri)
                    case4_dict[k4] = append_to_dict_list(case4_dict, k4, uri)
                    case5_dict[k5] = append_to_dict_list(case5_dict, k5, uri)
                    case6_dict[k6] = append_to_dict_list(case6_dict, k6, uri)

    return {
        CASE_0: case0_dict,
        CASE_1: case1_dict,
        CASE_2: case2_dict,
        CASE_3: case3_dict,
        CASE_4: case4_dict,
        CASE_5: case5_dict,
        CASE_6: case6_dict,
    }


def get_author_disambiguation_data(vivo_auth_disambig_data,
                                   last, first, middle):
    """
    @TODO: check if we can pass an object instead

    @see get_vivo_disambiguation_data_from_csv()
    :return an array of uri's that have been found in vivo for
    the specified person
    """
    vname = VivoName(last, first, middle)
    case = vname.get_case()
    disambiguation_list = vivo_auth_disambig_data[case].get(
        vname.get_key(), [])
    return disambiguation_list
