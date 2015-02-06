#!/usr/bin/env/python
""" Test cases for vivopump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.00"

import unittest
from vivopump import new_uri


class NewUriTestCase(unittest.TestCase):
    def test_new_uri(self):
        uri = new_uri()
        self.assertTrue(len(uri) > 0)

if __name__ == "__main__":
    unittest.main()

