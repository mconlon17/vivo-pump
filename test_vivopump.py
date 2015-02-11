#!/usr/bin/env/python
# coding=utf-8
""" test_vivopump.py -- Test cases for vivopump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.00"

import unittest
from vivopump import new_uri, read_csv, vivo_query, repair_email, repair_phone_number, comma_space, improve_title, \
    improve_dollar_amount, InvalidDataException, improve_date, improve_deptid, improve_sponsor_award_id


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


class CommaSpaceTestCase(unittest.TestCase):
    def test_no_op(self):
        in_string = "A, okay"
        out_string = comma_space(in_string)
        self.assertEqual(in_string, out_string)

    def test_trailing_comma(self):
        in_string = "A, okay,"
        out_string = comma_space(in_string)
        self.assertEqual(in_string, out_string)

    def test_adding_spaces_after_commas(self):
        in_string = "one,two,three"
        out_string = comma_space(in_string)
        self.assertEqual("one, two, three", out_string)


class ImproveTitleTestCase(unittest.TestCase):
    def test_simple_substitution(self):
        in_title = " hiv in fla, a multi-ctr  trial  "
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual("HIV in Florida, a Multi-Center Trial", out_title)

    def test_substitution_at_end(self):
        in_title = "Agricultural Engineering Bldg"
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual("Agricultural Engineering Building", out_title)

    def test_preserve_unicode(self):
        in_title = u"François Börner"
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual(u"François Börner", out_title)

    def test_comma_spacing(self):
        in_title = "a big,fat comma"
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual("A Big, Fat Comma", out_title)

    def test_apostrophe(self):
        in_title = "Tom's"
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual("Tom's", out_title)


class ImproveDollarAmountTestCase(unittest.TestCase):
    def test_no_op(self):
        in_string = "1234.56"
        out_string = improve_dollar_amount(in_string)
        self.assertEqual(in_string, out_string)

    def test_remove_chars(self):
        in_string = "$1,234.56"
        out_string = improve_dollar_amount(in_string)
        self.assertEqual("1234.56", out_string)

    def test_add_cents(self):
        in_string = "123"
        out_string = improve_dollar_amount(in_string)
        self.assertEqual("123.00", out_string)

    def test_invalid_data(self):
        in_string = "A6"
        with self.assertRaises(InvalidDataException):
            out_string = improve_dollar_amount(in_string)
            print out_string


class ImproveDateTestCase(unittest.TestCase):
    def test_no_op(self):
        in_string = "2014-12-09"
        out_string = improve_date(in_string)
        self.assertEqual(in_string, out_string)

    def test_short(self):
        in_string = "14-12-9"
        out_string = improve_date(in_string)
        self.assertEqual("2014-12-09", out_string)

    def test_separators(self):
        in_string = "34/2/1"
        out_string = improve_date(in_string)
        self.assertEqual("2034-02-01", out_string)

    def test_invalid_data(self):
        in_string = "A6"
        with self.assertRaises(InvalidDataException):
            out_string = improve_date(in_string)
            print out_string

    def test_month_word(self):
        in_string = "15-aug-9"
        out_string = improve_date(in_string)
        self.assertEqual("2015-08-09", out_string)

    def test_invalid_data(self):
        in_string = "15-alg-9"
        with self.assertRaises(InvalidDataException):
            out_string = improve_date(in_string)
            print out_string


class ImproveDeptIdTestCase(unittest.TestCase):
    def test_no_op(self):
        in_string = "16350100"
        out_string = improve_deptid(in_string)
        self.assertEqual(in_string, out_string)

    def test_short(self):
        in_string = "1234567"
        out_string = improve_deptid(in_string)
        self.assertEqual("01234567", out_string)

    def test_invalid_data(self):
        in_string = "A6"
        with self.assertRaises(InvalidDataException):
            out_string = improve_deptid(in_string)
            print out_string


class ImproveSponsorAwardIdTestCase(unittest.TestCase):
    def test_no_op(self):
        in_string = "14 A 76 Jan 2009"
        out_string = improve_sponsor_award_id(in_string)
        self.assertEqual(in_string, out_string)

    def test_strip(self):
        in_string = "  1234567 "
        out_string = improve_sponsor_award_id(in_string)
        self.assertEqual("1234567", out_string)

    def test_nih(self):
        in_string = "5R01 DK288283 "
        out_string = improve_sponsor_award_id(in_string)
        self.assertEqual("R01DK288283", out_string)

    def test_nih_upper(self):
        in_string = "5r01 Dk288283 "
        out_string = improve_sponsor_award_id(in_string)
        self.assertEqual("R01DK288283", out_string)


if __name__ == "__main__":
    unittest.main()