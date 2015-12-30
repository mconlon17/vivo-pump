#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_utils.py -- Test functions in utils.py
"""

import unittest
from disambiguate import utils

__author__ = "Andrei Sura"

FILE_NAME = 'test/vivo_people.csv'


class UtilsTests(unittest.TestCase):

    def test_append_to_dict_list(self):
        """
        Verify that we can append to the list in the dictionary
        """
        d = {'a': ['1']}
        # d_copy = {'a': ['1']}
        actual = utils.append_to_dict_list(d, 'a', 2)
        expected = ['1', 2]
        self.assertEquals(actual, expected)
        # self.assertEquals(d, d_copy)

        actual = utils.append_to_dict_list(d, 'x', 99)
        self.assertEquals(actual, [99])

    def test_get_vivo_disambiguation_data_from_csv(self):
        """
        Verify that we can parse the static file containing the
        current list of people in vivo (UF data in csv format ~20MB)

        person_uri, fname,  lname,   mname
        uri_1,      First,  Last,    Middle
        uri_2,      First,  Last,   X
        uri_3,      Aww,    B,
        """
        expected = {
            0: {
                'last':         ['uri_1', 'uri_2'],
                'b':            ['uri_3'],
            },
            1: {
                'last|f':       ['uri_1', 'uri_2'],
                'b|a':          ['uri_3']
            },
            2: {
                'last|first':   ['uri_1', 'uri_2'],
                'b|aww':        ['uri_3']
            },
            3: {
                'last|f|m':     ['uri_1'],
                'last|f|x':     ['uri_2'],
            },
            4: {
                'last|f|middle':    ['uri_1'],
                'last|f|x':         ['uri_2']
            },
            5: {
                'last|first|m':      ['uri_1'],
                'last|first|x':      ['uri_2']
            },
            6: {
                'last|first|middle':    ['uri_1'],
                'last|first|x':         ['uri_2']
            }
        }

        actual = utils.get_vivo_disambiguation_data_from_csv(FILE_NAME)
        # import pprint
        # pprint.pprint(actual + expected)
        # pprint.pprint(expected)
        self.assertEquals(expected, actual)


if __name__ == '__main__':
    unittest.main()
