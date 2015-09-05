#!/usr/bin/env/python
# coding=utf-8
""" test_sv.py -- Test cases for Simple VIVO
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "1.00"

import unittest
from vivopump import new_uri, read_csv, vivo_query, write_update_def, improve_email, improve_phone_number, comma_space, \
    improve_title, make_update_query, read_update_def, make_rdf_term, get_graph, \
    improve_dollar_amount, InvalidDataException, improve_date, improve_deptid, improve_sponsor_award_id
from pump import Pump


class ParamTestCase(unittest.TestCase):
    def test_parameters(self):
        uri = new_uri()
        self.assertTrue(len(uri) > 0)

if __name__ == "__main__":
    unittest.main()