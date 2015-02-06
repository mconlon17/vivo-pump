#!/usr/bin/env/python
""" test_vivopump.py -- Test cases for vivopump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.00"

import unittest
from vivopump import new_uri, read_csv, vivo_query


class NewUriTestCase(unittest.TestCase):
    def test_new_uri(self):
        uri = new_uri()
        print uri
        self.assertTrue(len(uri) > 0)


class ReadCSVKeysTestCase(unittest.TestCase):
    def test_read_csv_keys(self):
        data = read_csv("extension.txt")
        print data.keys()
        self.assertTrue(data.keys() == range(1, 74))


class VIVOQueryTestCase(unittest.TestCase):
    def test_vivo_query(self):
        result = ""
        result = vivo_query("SELECT ?uri WHERE { ?uri a foaf:Organization .}")
        print result
        self.assertTrue(len(result) > 0)


if __name__ == "__main__":
    unittest.main()

