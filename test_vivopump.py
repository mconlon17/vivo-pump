#!/usr/bin/env/python
""" test_vivopump.py -- Test cases for vivopump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.00"

import unittest
from vivopump import new_uri, read_csv, vivo_query, repair_email, repair_phone_number


class NewUriTestCase(unittest.TestCase):
    def test_new_uri(self):
        uri = new_uri()
        self.assertTrue(len(uri) > 0)


class ReadCSVKeysTestCase(unittest.TestCase):
    def test_read_csv_keys(self):
        data = read_csv("extension.txt")
        self.assertTrue(data.keys() == range(1, 74))


class VIVOQueryTestCase(unittest.TestCase):
    def test_vivo_query(self):
        result = vivo_query("SELECT ?uri WHERE { ?uri a foaf:Organization .}")
        self.assertTrue(len(result) > 0)


class RepairEmailTestCase(unittest.TestCase):
    def test_no_op(self):
        in_email = "mconlon@ufl.edu"
        out_email = repair_email(in_email)
        self.assertEqual(in_email, out_email)


class RepairPhoneNumberTestCase(unittest.TestCase):
    def test_no_op(self):
        in_phone = "(352) 273-8700"
        out_phone = repair_phone_number(in_phone)
        self.assertEqual(in_phone, out_phone)

    def test_uf_special(self):
        in_phone = "3-8700"
        out_phone = repair_phone_number(in_phone)
        self.assertEqual("(352) 273-8700", out_phone)


if __name__ == "__main__":
    unittest.main()

