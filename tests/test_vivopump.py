#!/usr/bin/env/python
# coding=utf-8
""" test_vivopump.py -- Test cases for vivopump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "1.00"

import unittest
from vivopump import new_uri, read_csv, write_csv, vivo_query, write_update_def, improve_email, improve_phone_number, \
    comma_space, read_csv_fp, write_csv_fp, get_vivo_ufid, get_vivo_authors, get_vivo_types, get_vivo_sponsorid, \
    improve_title, make_update_query, read_update_def, make_rdf_term, get_graph, \
    improve_dollar_amount, InvalidDataException, improve_date, improve_deptid, improve_sponsor_award_id, \
    improve_jobcode_description, improve_course_title, replace_initials, parse_pages, parse_date_parts, \
    improve_display_name
from pump import Pump


class ReplaceInitialsCase(unittest.TestCase):
    def test_replace_initials_default(self):
        t = replace_initials('This is A. test')
        self.assertEqual(t, 'This is A test')

    def test_replace_initials_two(self):
        t = replace_initials('This is A. B. test')
        self.assertEqual(t, 'This is A B test')

    def test_replace_initials_consecutive_dots(self):
        t = replace_initials('This is A.. B. test')
        self.assertEqual(t, 'This is A. B test')

    def test_replace_initials_consecutive_initials(self):
        t = replace_initials('This is A.B. test')
        self.assertEqual(t, 'This is AB test')


class ParsePagesCase(unittest.TestCase):
    def test_parse_pages_default(self):
        [a, b] = parse_pages('30-55')
        print a, b
        self.assertEqual(a, '30')
        self.assertEqual(b, '55')

    def test_parse_pages_no_end(self):
        [a, b] = parse_pages('30')
        print a, b
        self.assertEqual(a, '30')
        self.assertEqual(b, '')


class ParseDatePartsCase(unittest.TestCase):
    def test_parse_date_parts_default(self):
        date = parse_date_parts('AUG', '2014')
        print date
        self.assertEqual(date, '2014-08-01T00:00:00')

    def test_parse_date_parts_with_day(self):
        date = parse_date_parts('AUG 15', '2014')
        print date
        self.assertEqual(date, '2014-08-15T00:00:00')

    def test_parse_date_parts_with_months(self):
        date = parse_date_parts('JUL-AUG', '2014')
        print date
        self.assertEqual(date, '2014-07-01T00:00:00')


class NewUriTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
             'username': 'vivo_root@school.edu', 'password': 'v;bisons',
             'uriprefix': 'http://vivo.school.edu/individual/n'}

    def test_new_uri_default(self):
        uri = new_uri(NewUriTestCase.parms)
        print uri
        self.assertTrue(len(uri) > 0)

    def test_new_uri_prefix(self):
        parms = NewUriTestCase.parms
        parms['uriprefix'] = 'http://my.vivo.edu/'
        uri = new_uri(parms)
        print uri
        self.assertTrue(uri.startswith('http://my.vivo.edu'))


class ReadUpdateDefTestCase(unittest.TestCase):
    def test_read_normal_def(self):
        update_def = read_update_def('data/grant_def.json')
        self.assertTrue(update_def.keys() == ['entity_def', 'column_defs'])

    def test_update_def_order(self):
        update_def = read_update_def('data/grant_def.json')
        self.assertEqual(update_def['entity_def']['order'][0:4], [u'deptid', u'direct_costs', u'cois', u'end_date'])


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
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
             'username': 'vivo_root@school.edu', 'password': 'v;bisons',
             'uriprefix': 'http://vivo.school.edu/individual/n'}

    def test_normal_case(self):
        update_def = read_update_def('data/grant_def.json')
        a = get_graph(update_def, GetGraphTestCase.parms)
        print len(a)
        self.assertTrue(len(a) == 11)


class ReadCSVTestCase(unittest.TestCase):
    def test_read_csv_keys(self):
        data = read_csv("data/extension.txt", delimiter='\t')
        print data
        self.assertTrue(data.keys() == range(1, 74))

    def test_read_csv_minimal(self):
        data = read_csv("data/minimal.txt", delimiter='|')
        data_string = "{1: {u'overview': u'None', u'uri': u'http://vivo.ufl.edu/individual/n7023304'}}"
        self.assertEqual(data_string, str(data))

    def test_read_csv_fp(self):
        fp = open("data/minimal.txt", 'rU')
        data = read_csv_fp(fp, delimiter='|')
        fp.close()
        data_string = "{1: {u'overview': u'None', u'uri': u'http://vivo.ufl.edu/individual/n7023304'}}"
        self.assertEqual(data_string, str(data))


class WriteCSVTestCase(unittest.TestCase):
    def test_write_csv(self):
        data = read_csv("data/buildings.txt", delimiter='\t')
        write_csv("data/buildings_out.txt", data, delimiter='\t')
        data2 = read_csv("data/buildings.txt", delimiter='\t')
        self.assertTrue(data == data2)

    def test_write_csv_fp(self):
        data = read_csv("data/buildings.txt", delimiter='\t')
        fp = open('data/buildings_out.txt', 'w')
        write_csv_fp(fp, data, delimiter='\t')
        fp.close()
        data2 = read_csv("data/buildings.txt", delimiter='\t')
        self.assertTrue(data == data2)


class VIVOQueryTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
             'username': 'vivo_root@school.edu', 'password': 'v;bisons'}

    def test_vivo_query(self):
        result = vivo_query("""
        SELECT ?label
        WHERE { <http://vivo.school.edu/individual/n1133> rdfs:label ?label }
        """, VIVOQueryTestCase.parms, debug=True)
        print result
        self.assertTrue(len(result) > 0)

    def test_bad_request(self):
        from SPARQLWrapper import SPARQLExceptions
        with self.assertRaises(SPARQLExceptions.QueryBadFormed):
            result = vivo_query("""
            SEWECT ?label
            WHERE { <http://vivo.ufl.edu/individual/n25562> rdfs:label ?label }
            """, VIVOQueryTestCase.parms, debug=True)
            print result


class VIVOGetTypesTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
             'username': 'vivo_root@school.edu', 'password': 'v;bisons'}

    def test_vivo_get_types(self):
        result = get_vivo_types("?uri a foaf:Person .", VIVOGetTypesTestCase.parms)
        self.assertTrue(len(result) > 0)


class VIVOGetUFIDTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
             'username': 'vivo_root@school.edu', 'password': 'v;bisons'}

    def test_vivo_get_ufid(self):
        result = get_vivo_ufid(VIVOGetUFIDTestCase.parms)
        self.assertTrue(len(result) > 0)


class VIVOGetAuthorsTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
             'username': 'vivo_root@school.edu', 'password': 'v;bisons'}

    def test_vivo_get_authors(self):
        result = get_vivo_authors(VIVOGetAuthorsTestCase.parms)
        self.assertTrue(len(result) > 0)


class VIVOGetSponsorsTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
             'username': 'vivo_root@school.edu', 'password': 'v;bisons'}

    def test_vivo_get_sponsorid(self):
        result = get_vivo_sponsorid(VIVOGetSponsorsTestCase.parms)
        print len(result)
        self.assertTrue(len(result) > 0)


class WriteUpdateDefTestCase(unittest.TestCase):
    def test_create_file(self):
        import os.path

        update_def = "{}"
        filename = "__write_update_def_test_create_file.json"
        write_update_def(update_def, filename)
        self.assertTrue(os.path.isfile(filename))
        os.remove(filename)


class ImproveEmailTestCase(unittest.TestCase):
    def test_no_op(self):
        in_email = "mconlon@ufl.edu"
        out_email = improve_email(in_email)
        self.assertEqual(in_email, out_email)


class ImproveDisplayNameTestCase(unittest.TestCase):
    def test_no_op(self):
        in_name = "Conlon, Mike"
        out_name = improve_display_name(in_name)
        self.assertEqual(in_name, out_name)

    def test_standard_case(self):
        in_name = "CONLON,MIKE"
        out_name = improve_display_name(in_name)
        self.assertEqual("Conlon, Mike", out_name)


class ImprovePhoneNumberTestCase(unittest.TestCase):
    def test_no_op(self):
        in_phone = "(352) 273-8700"
        out_phone = improve_phone_number(in_phone)
        self.assertEqual(in_phone, out_phone)

    def test_uf_special(self):
        in_phone = "3-8700"
        out_phone = improve_phone_number(in_phone)
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


class ImproveJobCodeDescriptionTestCase(unittest.TestCase):
    def test_simple_substitution(self):
        in_title = "ASST PROF"
        out_title = improve_jobcode_description(in_title)
        print out_title
        self.assertEqual("Assistant Professor", out_title)

    def test_substitution_at_end(self):
        in_title = "RES ASO PROF & DIR"
        out_title = improve_jobcode_description(in_title)
        print out_title
        self.assertEqual("Research Associate Professor  and  Director", out_title)

    def test_preserve_unicode(self):
        in_title = u"CRD TECH PRG 2"
        out_title = improve_jobcode_description(in_title)
        print out_title
        self.assertEqual(u"Coordinator Technician Program 2", out_title)


class ImproveCourseTitleTestCase(unittest.TestCase):
    def test_simple_substitution(self):
        in_title = "INTRO TO STAT"
        out_title = improve_course_title(in_title)
        print out_title
        self.assertEqual("Introduction to Statistics", out_title)

    def test_substitution_at_end(self):
        in_title = "HIST OF HLTHCARE"
        out_title = improve_course_title(in_title)
        print out_title
        self.assertEqual("History of Healthcare", out_title)

    def test_preserve_unicode(self):
        in_title = u"SPEC TOP IN PRAC"
        out_title = improve_course_title(in_title)
        print out_title
        self.assertEqual(u"Special Topics in Practice", out_title)


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
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
             'username': 'vivo_root@school.edu', 'password': 'v;bisons'}

    def test_pump_serialize(self):
        p = Pump(query_parms=PumpTestCase.parms)
        self.assertTrue(p.serialize().startswith("{\"entity_def\":"))

    def test_pump_filename(self):
        p = Pump("data/building_def.json", query_parms=PumpTestCase.parms)
        self.assertTrue("vivo:Building" in p.serialize())

    def test_pump_summarize(self):
        p = Pump("data/building_def.json", query_parms=PumpTestCase.parms)
        result = p.summarize()
        print result
        self.assertTrue("Pump Summary for data/building" in result)

    def test_pump_get_no_filename(self):
        p = Pump("data/building_def.json", query_parms=PumpTestCase.parms)
        with self.assertRaises(TypeError):
            n_rows = p.get()
            print n_rows

    def test_pump_get(self):
        p = Pump("data/building_def.json", query_parms=PumpTestCase.parms)
        n_rows = p.get("data/buildings.txt")
        print n_rows
        self.assertEqual(2, n_rows)

    def test_pump_update(self):
        p = Pump("data/building_def.json")
        [add, sub] = p.update("data/buildings.txt")
        self.assertEqual(0, len(add))
        self.assertEqual(0, len(sub))


class PumpGetTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
        'username': 'vivo_root@school.edu', 'password': 'v;bisons'}

    def test_get_no_filter(self, ):
        p = Pump("data/building_def.json", query_parms=PumpGetTestCase.parms)
        p.filter = False
        n_rows = p.get("data/buildings_nofilter.txt")
        self.assertEqual(2, n_rows)

    def test_get_filter(self):
        p = Pump("data/building_def.json", query_parms=PumpGetTestCase.parms)
        n_rows = p.get("data/buildings_filtered.txt")
        self.assertEqual(2, n_rows)


class PumpUpdateCallTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
        'username': 'vivo_root@school.edu', 'password': 'v;bisons',
        'uriprefix': 'http://vivo.school.edu/individual/'}

    def test_default_usage(self):
        p = Pump(query_parms=PumpUpdateCallTestCase.parms)
        p.update()
        self.assertTrue("data/pump_def.json" in p.summarize())  # Using the default definition

    def test_no_update_file(self):
        p = Pump(query_parms=PumpUpdateCallTestCase.parms)
        with self.assertRaises(IOError):
            p.update('data/no_update_file.txt')

    def test_normal_inject(self):
        p = Pump(query_parms=PumpUpdateCallTestCase.parms)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n8984374104', u'abbreviation': u'None'}}
        p.update()
        self.assertTrue("8984374104" in str(p.update_data))  # Using the injected data, not default

    def test_missing_uri_column_inject(self):
        p = Pump(query_parms=PumpUpdateCallTestCase.parms)
        p.update_data = {1: {u'overview': u'None'}}
        with self.assertRaises(KeyError):
            p.update()

    def test_inject_empty_original_graph(self):
        from rdflib import Graph, URIRef
        p = Pump(query_parms=PumpUpdateCallTestCase.parms,verbose=True)
        p.original_graph = Graph()
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n8984374104', u'abbreviation': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (None,
                                                 URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                                                 URIRef("http://vivoweb.org/ontology/core#Building")) in add)


class PumpUpdateLiteralsTestCase(unittest.TestCase):
    parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
        'username': 'vivo_root@school.edu', 'password': 'v;bisons',
        'uriprefix': 'http://vivo.school.edu/individual/'}

    def test_with_datatype(self):
        from rdflib import URIRef, Literal, XSD
        p = Pump("data/building_def.json", query_parms=PumpUpdateLiteralsTestCase.parms, verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n1001011525', u'abbreviation': u'PH9'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (URIRef("http://vivo.ufl.edu/individual/n1001011525"),
                                                 URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                                                 Literal("PH9", datatype=XSD.string)) in add)

    def test_with_lang(self):
        from rdflib import URIRef, Literal
        p = Pump("data/building_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n1001011525', u'name': u'Building 42'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (URIRef("http://vivo.ufl.edu/individual/n1001011525"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                                 Literal("Building 42", lang="en-US")) in add)

    def test_without_datatype(self):
        from rdflib import URIRef, Literal
        p = Pump("data/building_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n1001011525', u'url': u'http://a'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 4 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#linkURI"),
                                                 Literal("http://a")) in add)

    def test_without_lang(self):
        from rdflib import URIRef, Literal
        p = Pump("data/org_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n928712', u'name': u'Ad ver tising'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (URIRef("http://vivo.ufl.edu/individual/n928712"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                                 Literal("Ad ver tising")) in add)


class PumpUpdateDataTestCase(unittest.TestCase):
    def test_unique_one_add(self):
        from rdflib import URIRef, Literal
        p = Pump()
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n1001011525', u'abbreviation': u'PH9'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (URIRef("http://vivo.ufl.edu/individual/n1001011525"),
                                                 URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                                                 Literal("PH9")) in add)

    def test_unique_one_change(self):
        from rdflib import URIRef, Literal, XSD
        p = Pump()
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n111669', u'abbreviation': u'JWR2'}}
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
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n111669', u'abbreviation': u'None'}}
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

        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n7023301', u'zip': u'32653'}}
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
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n765319', u'zip': u'32653'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (URIRef("http://vivo.ufl.edu/individual/n119803"),
                                                 URIRef("http://vivoweb.org/ontology/core#addressPostalCode"),
                                                 Literal("32653")) in add)

    def test_unique_two_change(self):
        from rdflib import URIRef, Literal, XSD

        # Change the zip code on an existing address

        p = Pump("data/org_def.json")
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n87597', u'zip': u'32653'}}
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
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n87597', u'zip': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (URIRef("http://vivo.ufl.edu/individual/n994294"),
                                                 URIRef("http://vivoweb.org/ontology/core#addressPostalCode"),
                                                 Literal("32611", datatype=XSD.string)) in sub)

    def test_unique_two_delete_not_found(self):

        # Delete the zip code from an existing address that doesn't have a zip code.

        p = Pump("data/org_def.json")
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n765319', u'zip': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)

    def test_unique_three_add_fullpath(self):
        from rdflib import URIRef, Literal
        p = Pump("data/grant_def.json")

        # Add a start date to a grant.  There is no date time interval, so a full path will need to be created

        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n51914', u'start_date': u'2015-03-01'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 5 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2015-03-01")) in add)

    def test_unique_three_add_partial_path(self):
        from rdflib import URIRef, Literal
        p = Pump("data/grant_def.json", verbose=True)

        # WARNING.  This test passes by constructing a new datetime interval. Not clear if this is the desired result.

        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n42774', u'start_date': u'2006-03-01'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 5 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2006-03-01")) in add)

    def test_unique_three_change_no_xsd(self):
        from rdflib import URIRef, Literal
        p = Pump("data/grant_def.json", verbose=True)

        # WARNING.  This test passes by changing the start date value on an existing datetime interval.  Not sure
        # if this is the desired behavior.

        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n1240414034', u'start_date': u'2011-07-02'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2011-07-02")) in add and
                                                (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2011-07-01T00:00:00")) in sub)

    def test_unique_three_change_xsd(self):
        from rdflib import URIRef, Literal, XSD
        p = Pump("data/grant_def.json", verbose=True)

        # WARNING.  This test passes by changing the start date value on an existing datetime interval.  Not sure
        # if this is the desired behavior.

        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n650082272', u'start_date': u'2006-03-02'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2006-03-02")) in add and
                                                (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2006-07-01T00:00:00", datatype=XSD.dateTime)) in sub)

    def test_unique_three_delete(self):
        from rdflib import URIRef, Literal, XSD

        # WARNING: Delete start date value from existing datetime interval.  This may not be the desirable data
        # management action

        p = Pump("data/grant_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n650082272', u'start_date': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2006-07-01T00:00:00", datatype=XSD.dateTime)) in sub)

    def test_multiple_one_add(self):
        from rdflib import URIRef

        #  Add multiple values for an attribute to an entity that has no values for the attribute

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n1723097935',
                               u'research_areas': u'http://vivo.ufl.edu/individual/n2551317090;http://vivo.ufl.edu/individual/n157098'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 2 and len(sub) == 0 and (URIRef("http://vivo.ufl.edu/individual/n1723097935"),
                                                 URIRef("http://vivoweb.org/ontology/core#hasResearchArea"),
                                                 URIRef("http://vivo.ufl.edu/individual/n2551317090")) in add and
                                                (URIRef("http://vivo.ufl.edu/individual/n1723097935"),
                                                 URIRef("http://vivoweb.org/ontology/core#hasResearchArea"),
                                                 URIRef("http://vivo.ufl.edu/individual/n157098")) in add)

    def test_multiple_one_change_nothing(self):

        #  Do nothing if the multiple values specified match those in VIVO

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n1723097935',
                               u'types': u'person;thing;agent;fac;uf;ufc'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)

    def test_multiple_one_change(self):
        from rdflib import URIRef

        #  Change the set of values adding one and removing another

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n1723097935',
                               u'types': u'person;thing;agent;fac;uf;pd'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 1 and len(sub) == 1 and
                        (URIRef("http://vivo.ufl.edu/individual/n1723097935"),
                         URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                         URIRef("http://vivoweb.org/ontology/core#Postdoc")) in add and
                        (URIRef("http://vivo.ufl.edu/individual/n1723097935"),
                         URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                         URIRef("http://vivo.ufl.edu/ontology/vivo-ufl/UFCurrentEntity")) in sub)

    def test_multiple_one_delete(self):

        #  Empty the set of values

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n25674',
                               u'research_areas': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 4)


class PumpRemoveTestCase(unittest.TestCase):
    def test_small_case(self):
        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n2084211328',
                               u'remove': u'True'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 1)

    def test_large_case(self):
        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n25674',
                               u'remove': u'True'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 1)

    def test_not_found(self):
        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.ufl.edu/individual/n12345678',
                               u'remove': u'True'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)


class PumpEnumTestCase(unittest.TestCase):
    def test_normal_case(self):
        p = Pump("data/person_def.json", verbose=True)
        summary = p.summarize()
        self.assertTrue(summary.find('people_types') > -1)


if __name__ == "__main__":
    unittest.main()