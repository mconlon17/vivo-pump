# -*- coding: utf-8 -*-
"""
vivo_name.py - helper class for encapsulating the logic related to
    vivo name parsing
"""

__author__ = "Andrei Sura"

import sys

# divider for the fragments in the key
DIV = '|'

# constants used to distinguish between disambiguation cases
CASE_0 = 0
CASE_1 = 1
CASE_2 = 2
CASE_3 = 3
CASE_4 = 4
CASE_5 = 5
CASE_6 = 6


class VivoName(object):
    """
    Class constructor.

    @see setup()
    @see usage in
    """
    def __init__(self, last, first, middle):
        self.last = last.strip()
        self.first = first.strip()
        self.middle = middle.strip()
        self.case = 0
        self.setup()

    def get_case(self):
        return self.case

    @classmethod
    def format_as_key(self, key):
        if key is None:
            return 'none'

        try:
            return key.encode('utf-8', errors='ignore').strip().lower()
        except Exception as exc:
            # print >>sys.stderr, "KEY: " + key
            # sys.exit()
            pass
        return key.decode("utf8")

    def has_all_parts(self):
        return self.has_last() and self.has_first() and self.has_middle()

    def has_last(self):
        return len(self.last) > 0

    def has_first(self):
        return len(self.first) > 0

    def has_middle(self):
        return len(self.middle) > 0

    def setup(self):
        """
        Helper method for computing the `case` logic used for disambiguation.
        Called by the constructor.
        """
        if self.has_all_parts():
            if len(self.first) == 1 and len(self.middle) == 1:
                self.case = 3
            if len(self.first) == 1 and len(self.middle) > 1:
                self.case = 4
            if len(self.first) > 1 and len(self.middle) == 1:
                self.case = 5
            if len(self.first) > 1 and len(self.middle) > 1:
                self.case = 6
        elif self.has_last() and self.has_first():
            if len(self.first) == 1:
                self.case = 1
            else:
                self.case = 2
        else:
            self.case = 0

    def get_key_0(self):
        return self.format_as_key(self.last)

    def get_key_1(self):
        return self.format_as_key(self.last + DIV + self.first[0])

    def get_key_2(self):
        return self.format_as_key(self.last + DIV + self.first)

    def get_key_3(self):
        return self.format_as_key(self.last + DIV + self.first[0] +
                                  DIV + self.middle[0])

    def get_key_4(self):
        return self.format_as_key(self.last + DIV +
                                  self.first[0] + DIV + self.middle)

    def get_key_5(self):
        return self.format_as_key(self.last + DIV +
                                  self.first + DIV + self.middle[0])

    def get_key_6(self):
        return self.format_as_key(self.last + DIV +
                                  self.first + DIV + self.middle)

    def get_key(self):
        if CASE_0 == self.case:
            return self.get_key_0()
        if CASE_1 == self.case:
            return self.get_key_1()
        if CASE_2 == self.case:
            return self.get_key_2()
        if CASE_3 == self.case:
            return self.get_key_3()
        if CASE_4 == self.case:
            return self.get_key_4()
        if CASE_5 == self.case:
            return self.get_key_5()
        if CASE_6 == self.case:
            return self.get_key_6()


