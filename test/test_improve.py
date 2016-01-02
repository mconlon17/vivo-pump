#!/usr/bin/env/python
# coding=utf-8
"""
    test_improve.py -- Test cases for improve
"""

import unittest

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "0.1"


class ImproveEmailTestCase(unittest.TestCase):
    def test_no_op(self):
        from improve.improve import improve_email
        in_email = "mconlon@ufl.edu"
        out_email = improve_email(in_email)
        self.assertEqual(in_email, out_email)

    def test_format(self):
        from improve.improve import improve_email
        in_email = " Mconlon@ufl.edu "
        out_email = improve_email(in_email)
        self.assertEqual(out_email, "mconlon@ufl.edu")


class ImproveDisplayNameTestCase(unittest.TestCase):
    def test_no_op(self):
        from improve.improve import improve_display_name
        in_name = "Conlon, Mike"
        out_name = improve_display_name(in_name)
        self.assertEqual(in_name, out_name)

    def test_standard_case(self):
        from improve.improve import improve_display_name
        in_name = "CONLON,MIKE"
        out_name = improve_display_name(in_name)
        self.assertEqual("Conlon, Mike", out_name)


class ImprovePhoneNumberTestCase(unittest.TestCase):
    def test_no_op(self):
        from improve.improve import improve_phone_number
        in_phone = "(352) 273-8700"
        out_phone = improve_phone_number(in_phone)
        self.assertEqual(in_phone, out_phone)

    def test_uf_special(self):
        from improve.improve import improve_phone_number
        in_phone = "3-8700"
        out_phone = improve_phone_number(in_phone)
        self.assertEqual("(352) 273-8700", out_phone)


class CommaSpaceTestCase(unittest.TestCase):
    def test_no_op(self):
        from improve.improve import comma_space
        in_string = "A, okay"
        out_string = comma_space(in_string)
        self.assertEqual(in_string, out_string)

    def test_trailing_comma(self):
        from improve.improve import comma_space
        in_string = "A, okay,"
        out_string = comma_space(in_string)
        self.assertEqual(in_string, out_string)

    def test_adding_spaces_after_commas(self):
        from improve.improve import comma_space
        in_string = "one,two,three"
        out_string = comma_space(in_string)
        self.assertEqual("one, two, three", out_string)


class ImproveJobCodeDescriptionTestCase(unittest.TestCase):
    def test_simple_substitution(self):
        from improve.improve import improve_jobcode_description
        in_title = "ASST PROF"
        out_title = improve_jobcode_description(in_title)
        print out_title
        self.assertEqual("Assistant Professor", out_title)

    def test_substitution_at_end(self):
        from improve.improve import improve_jobcode_description
        in_title = "RES ASO PROF & DIR"
        out_title = improve_jobcode_description(in_title)
        print out_title
        self.assertEqual("Research Associate Professor and Director", out_title)

    def test_preserve_unicode(self):
        from improve.improve import improve_jobcode_description
        in_title = u"CRD TECH PRG 2"
        out_title = improve_jobcode_description(in_title)
        print out_title
        self.assertEqual(u"Coordinator Technician Program 2", out_title)


class ImproveCourseTitleTestCase(unittest.TestCase):
    def test_simple_substitution(self):
        from improve.improve import improve_course_title
        in_title = "INTRO TO STAT"
        out_title = improve_course_title(in_title)
        print out_title
        self.assertEqual("Introduction to Statistics", out_title)

    def test_substitution_at_end(self):
        from improve.improve import improve_course_title
        in_title = "HIST OF HLTHCARE"
        out_title = improve_course_title(in_title)
        print out_title
        self.assertEqual("History of Healthcare", out_title)

    def test_preserve_unicode(self):
        from improve.improve import improve_course_title
        in_title = u"SPEC TOP IN PRAC"
        out_title = improve_course_title(in_title)
        print out_title
        self.assertEqual(u"Special Topics in Practice", out_title)


class ImproveTitleTestCase(unittest.TestCase):
    def test_simple_substitution(self):
        from improve.improve import improve_title
        in_title = " hiv in fla, a multi-ctr  trial  "
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual("HIV in Florida, a Multi-Center Trial", out_title)

    def test_substitution_at_end(self):
        from improve.improve import improve_title
        in_title = "Agricultural Engineering Bldg"
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual("Agricultural Engineering Building", out_title)

    def test_preserve_unicode(self):
        from improve.improve import improve_title
        in_title = u"François Börner"
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual(u"François Börner", out_title)

    def test_comma_spacing(self):
        from improve.improve import improve_title
        in_title = "a big,fat comma"
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual("A Big, Fat Comma", out_title)

    def test_apostrophe(self):
        from improve.improve import improve_title
        in_title = "Tom's"
        out_title = improve_title(in_title)
        print out_title
        self.assertEqual("Tom's", out_title)


class ImproveDollarAmountTestCase(unittest.TestCase):
    def test_no_op(self):
        from improve.improve import improve_dollar_amount
        in_string = "1234.56"
        out_string = improve_dollar_amount(in_string)
        self.assertEqual(in_string, out_string)

    def test_remove_chars(self):
        from improve.improve import improve_dollar_amount
        in_string = "$1,234.56"
        out_string = improve_dollar_amount(in_string)
        self.assertEqual("1234.56", out_string)

    def test_add_cents(self):
        from improve.improve import improve_dollar_amount
        in_string = "123"
        out_string = improve_dollar_amount(in_string)
        self.assertEqual("123.00", out_string)

    def test_invalid_data(self):
        from improve.improve import improve_dollar_amount, InvalidDataException
        in_string = "A6"
        with self.assertRaises(InvalidDataException):
            out_string = improve_dollar_amount(in_string)
            print out_string


class ImproveDateTestCase(unittest.TestCase):
    def test_no_op(self):
        from improve.improve import improve_date
        in_string = "2014-12-09"
        out_string = improve_date(in_string)
        self.assertEqual(in_string, out_string)

    def test_short(self):
        from improve.improve import improve_date
        in_string = "14-12-9"
        out_string = improve_date(in_string)
        self.assertEqual("2014-12-09", out_string)

    def test_separators(self):
        from improve.improve import improve_date
        in_string = "34/2/1"
        out_string = improve_date(in_string)
        self.assertEqual("2034-02-01", out_string)

    def test_invalid_data(self):
        from improve.improve import improve_date, InvalidDataException
        in_string = "A6"
        with self.assertRaises(InvalidDataException):
            out_string = improve_date(in_string)
            print out_string

    def test_month_word(self):
        from improve.improve import improve_date
        in_string = "15-aug-9"
        out_string = improve_date(in_string)
        self.assertEqual("2015-08-09", out_string)

    def test_more_invalid_data(self):
        from improve.improve import improve_date, InvalidDataException
        in_string = "15-alg-9"
        with self.assertRaises(InvalidDataException):
            out_string = improve_date(in_string)
            print out_string


class ImproveDeptIdTestCase(unittest.TestCase):
    def test_no_op(self):
        from improve.improve import improve_deptid
        in_string = "16350100"
        out_string = improve_deptid(in_string)
        self.assertEqual(in_string, out_string)

    def test_short(self):
        from improve.improve import improve_deptid
        in_string = "1234567"
        out_string = improve_deptid(in_string)
        self.assertEqual("01234567", out_string)

    def test_invalid_data(self):
        from improve.improve import improve_deptid, InvalidDataException
        in_string = "A6"
        with self.assertRaises(InvalidDataException):
            out_string = improve_deptid(in_string)
            print out_string


class ImproveSponsorAwardIdTestCase(unittest.TestCase):
    def test_no_op(self):
        from improve.improve import improve_sponsor_award_id
        in_string = "14 A 76 Jan 2009"
        out_string = improve_sponsor_award_id(in_string)
        self.assertEqual(in_string, out_string)

    def test_strip(self):
        from improve.improve import improve_sponsor_award_id
        in_string = "  1234567 "
        out_string = improve_sponsor_award_id(in_string)
        self.assertEqual("1234567", out_string)

    def test_nih(self):
        from improve.improve import improve_sponsor_award_id
        in_string = "5R01 DK288283 "
        out_string = improve_sponsor_award_id(in_string)
        self.assertEqual("R01DK288283", out_string)

    def test_nih_upper(self):
        from improve.improve import improve_sponsor_award_id
        in_string = "5r01 Dk288283 "
        out_string = improve_sponsor_award_id(in_string)
        self.assertEqual("R01DK288283", out_string)
