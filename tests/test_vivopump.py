#!/usr/bin/env/python
# coding=utf-8
""" test_vivopump.py -- Test cases for vivopump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.00"

import unittest
from vivopump import new_uri, read_csv, vivo_query, write_update_def, repair_email, repair_phone_number, comma_space, \
    improve_title, make_update_query, read_update_def, make_rdf_term, get_graph, \
    improve_dollar_amount, InvalidDataException, improve_date, improve_deptid, improve_sponsor_award_id
from pump import Pump


class NewUriTestCase(unittest.TestCase):
    def test_new_uri(self):
        uri = new_uri()
        self.assertTrue(len(uri) > 0)


class ReadUpdateDefTestCase(unittest.TestCase):
    def test_read_normal_def(self):
        update_def = read_update_def('data/grant_def.json')
        print update_def
        self.assertTrue(update_def.keys() == ['entity_def', 'column_defs'])


class MakeUpdateQueryTestCase(unittest.TestCase):
    def test_make_query(self):
        update_def = read_update_def('data/grant_def.json')
        for path in update_def['column_defs'].values():
            update_query = make_update_query(update_def['entity_def']['entity_sparql'], path)
            print update_query
            self.assertTrue(len(update_query) > 0)


class MakeRdfTermTestCase(unittest.TestCase):
    def test_uriref_case(self):
        from rdflib import URIRef
        input_dict = {
            "type": "uri",
            "value": "http://vivo.ufl.edu/individual/n531532305"
        }
        rdf_term = make_rdf_term(input_dict)
        print rdf_term
        self.assertTrue(type(rdf_term) is URIRef)


class GetGraphTestCase(unittest.TestCase):
    def test_normal_case(self):
        update_def = read_update_def('data/grant_def.json')
        a = get_graph(update_def)
        print len(a)
        self.assertTrue(len(a) == 241611)


class ReadCSVTestCase(unittest.TestCase):
    def test_read_csv_keys(self):
        data = read_csv("data/extension.txt", delimiter='\t')
        print data
        self.assertTrue(data.keys() == range(1, 74))

    def test_read_csv_minimal(self):
        data = read_csv("data/minimal.txt", delimiter='\t')
        data_string = "{1: {u'overview': u'None', u'uri': u'<http://vivo.ufl.edu/individual/n7023304>'}}"
        self.assertEqual(data_string, str(data))


class VIVOQueryTestCase(unittest.TestCase):
    def test_vivo_query(self):
        result = vivo_query("""
        SELECT ?label
        WHERE { <http://vivo.ufl.edu/individual/n25562> rdfs:label ?label }
        """, debug=True)
        print result
        self.assertTrue(len(result) > 0)

    def test_bad_request(self):
        from SPARQLWrapper import SPARQLExceptions
        with self.assertRaises(SPARQLExceptions.QueryBadFormed):
            result = vivo_query("""
            SEWECT ?label
            WHERE { <http://vivo.ufl.edu/individual/n25562> rdfs:label ?label }
            """, debug=True)
            print result


class WriteUpdateDefTestCase(unittest.TestCase):
    def test_create_file(self):
        import os.path

        update_def = "{}"
        filename = "__write_update_def_test_create_file.json"
        write_update_def(update_def, filename)
        self.assertTrue(os.path.isfile(filename))
        os.remove(filename)


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


class PumpTestCase(unittest.TestCase):
    def test_pump_serialize(self):
        p = Pump()
        self.assertTrue(p.serialize().startswith("{\"entity_def\":"))

    def test_pump_filename(self):
        p = Pump("data/building_def.json")
        self.assertTrue("vivo:Building" in p.serialize())

    def test_pump_summarize(self):
        p = Pump("data/building_def.json")
        result = p.summarize()
        print result
        self.assertTrue("Pump Summary for data/building" in result)

    def test_pump_get_no_filename(self):
        p = Pump("data/building_def.json")
        with self.assertRaises(TypeError):
            n_rows = p.get()
            print n_rows

    def test_pump_get(self):
        p = Pump("data/building_def.json")
        n_rows = p.get("data/buildings.txt")
        print n_rows
        self.assertEqual(951, n_rows)

    def test_pump_update(self):
        p = Pump("data/building_def.json")
        [add, sub] = p.update("data/buildings.txt")
        self.assertEqual(74, len(add))
        self.assertEqual(76, len(sub))


class PumpUpdateCallTestCase(unittest.TestCase):
    def test_default_usage(self):
        p = Pump()
        p.update()
        self.assertTrue("data/pump_def.json" in p.summarize())  # Using the default definition

    def test_no_update_file(self):
        p = Pump()
        with self.assertRaises(IOError):
            p.update('data/no_update_file.txt')

    def test_normal_inject(self):
        p = Pump()
        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n8984374104', u'abbreviation': u'None'}}
        p.update()
        self.assertTrue("8984374104" in str(p.update_data))  # Using the injected data, not default

    def test_missing_uri_column_inject(self):
        p = Pump()
        p.update_data = {'1': {u'overview': u'None'}}
        with self.assertRaises(KeyError):
            p.update()


class PumpUpdateDataTestCase(unittest.TestCase):
    def test_unique_one_add(self):
        from rdflib import URIRef, Literal
        p = Pump()
        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n1001011525', u'abbreviation': u'PH9'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (URIRef("http://vivo.ufl.edu/individual/n1001011525"),
                                                 URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                                                 Literal("PH9")) in add)

    def test_unique_one_change(self):
        from rdflib import URIRef, Literal, XSD
        p = Pump()
        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n111669', u'abbreviation': u'JWR2'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and (URIRef("http://vivo.ufl.edu/individual/n111669"),
                               URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                               Literal("JWR2")) in add and
            len(sub) == 1 and (URIRef("http://vivo.ufl.edu/individual/n111669"),
                               URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                               Literal("JWRU", datatype=XSD.string)) in sub)

    def test_unique_one_delete(self):
        from rdflib import URIRef, Literal, XSD
        p = Pump()
        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n111669', u'abbreviation': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (URIRef("http://vivo.ufl.edu/individual/n111669"),
                                                 URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                                                 Literal("JWRU", datatype=XSD.string)) in sub)

    def test_unique_two_add_fullpath(self):
        from rdflib import URIRef, Literal
        p = Pump("data/org_def.json")

        # Add a zip code to Lee County Extension Office.  There is no address, so a full path will need
        # to be created

        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n7023301', u'zip': u'32653'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 4 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#addressPostalCode"),
                                                 Literal("32653")) in add)

    def test_unique_two_add_to_existing(self):
        from rdflib import URIRef, Literal

        # Add a zip code to the provost's office at UF.  An address already exists, the zip needs to be
        # added to the existing address

        p = Pump("data/org_def.json")
        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n765319', u'zip': u'32653'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (URIRef("http://vivo.ufl.edu/individual/n119803"),
                                                 URIRef("http://vivoweb.org/ontology/core#addressPostalCode"),
                                                 Literal("32653")) in add)

    def test_unique_two_change(self):
        from rdflib import URIRef, Literal, XSD

        # Change the zip code on an existing address

        p = Pump("data/org_def.json")
        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n87597', u'zip': u'32653'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (URIRef("http://vivo.ufl.edu/individual/n994294"),
                                                 URIRef("http://vivoweb.org/ontology/core#addressPostalCode"),
                                                 Literal("32653")) in add and
                                                (URIRef("http://vivo.ufl.edu/individual/n994294"),
                                                 URIRef("http://vivoweb.org/ontology/core#addressPostalCode"),
                                                 Literal("32611", datatype=XSD.string)) in sub)

    def test_unique_two_delete(self):
        from rdflib import URIRef, Literal, XSD

        # Delete the zip code on an existing address

        p = Pump("data/org_def.json")
        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n87597', u'zip': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (URIRef("http://vivo.ufl.edu/individual/n994294"),
                                                 URIRef("http://vivoweb.org/ontology/core#addressPostalCode"),
                                                 Literal("32611", datatype=XSD.string)) in sub)

    def test_unique_two_delete_not_found(self):

        # Delete the zip code from an existing address that doesn't have a zip code.

        p = Pump("data/org_def.json")
        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n765319', u'zip': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)

    def test_unique_three_add_fullpath(self):
        from rdflib import URIRef, Literal
        p = Pump("data/grant_def.json")

        # Add a start date to a grant.  There is no date time interval, so a full path will need to be created

        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n51914', u'start_date': u'2015-03-01'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 5 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2015-03-01")) in add)

    def test_unique_three_add_partial_path(self):
        from rdflib import URIRef, Literal
        p = Pump("data/grant_def.json", verbose=True)

        # Add a start date to an existing datetime interval that does not have one.  WARNING -- not clear that this
        # is best practice for data management.  Pump might include "no add" feature to prevent first class objects
        # from being tampered by updates.  The same dti might be used by two grants.  When is an entity a first
        # first class (like a datetime value?) and when is it like a blank node (vcard?) and when is it unclear (dti?)
        # VIVO does not explicitly use blank nodes, so this information needs to be stored externally??

        p.update_data = {'1': {u'uri': u'http://vivo.ufl.edu/individual/n42774', u'start_date': u'2006-03-01'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 3 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2006-03-01")) in add)


if __name__ == "__main__":
    unittest.main()