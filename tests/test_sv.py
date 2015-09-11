#!/usr/bin/env/python
# coding=utf-8
""" test_sv.py -- Test cases for Simple VIVO
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "1.00"

import unittest
from vivopump import get_parms


class ParamTestCase(unittest.TestCase):
    def test_parameters(self):
        parms = get_parms()
        self.assertTrue(len(parms) > 0)

if __name__ == "__main__":
    unittest.main()