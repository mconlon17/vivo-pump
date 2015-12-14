#!/usr/bin/env/python
# coding=utf-8
"""
    test_vivopump.py -- Test cases for vivopump
"""

import unittest
from vivopump import new_uri, read_csv, write_csv, vivo_query, write_update_def, improve_email, improve_phone_number, \
    comma_space, read_csv_fp, write_csv_fp, get_vivo_ufid, get_vivo_authors, get_vivo_types, get_vivo_sponsorid, \
    improve_title, make_update_query, read_update_def, make_rdf_term, get_graph, \
    improve_dollar_amount, InvalidDataException, InvalidDefException, PathLengthException, improve_date, \
    improve_deptid, improve_sponsor_award_id, improve_jobcode_description, improve_course_title, replace_initials, \
    parse_pages, parse_date_parts, improve_display_name
from pump import Pump

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "1.00"


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
    query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                   'username': 'vivo_root@school.edu',
                   'password': 'v;bisons',
                   'uriprefix': 'http://vivo.school.edu/individual/n',
                   'prefix': ('PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>'
                              'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
                              'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>'
                              'PREFIX owl: <http://www.w3.org/2002/07/owl#>'
                              'PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>'
                              'PREFIX bibo: <http://purl.org/ontology/bibo/>'
                              'PREFIX event: <http://purl.org/NET/c4dm/event.owl#>'
                              'PREFIX foaf: <http://xmlns.com/foaf/0.1/>'
                              'PREFIX obo: <http://purl.obolibrary.org/obo/>'
                              'PREFIX skos: <http://www.w3.org/2004/02/skos/core#>'
                              'PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>'
                              'PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>'
                              'PREFIX vivo: <http://vivoweb.org/ontology/core#>')
                   }

    def test_new_uri_default(self):
        uri = new_uri(NewUriTestCase.query_parms)
        print uri
        self.assertTrue(len(uri) > 0)

    def test_new_uri_prefix(self):
        parms = NewUriTestCase.query_parms
        parms['uriprefix'] = 'http://my.vivo.edu/date'
        uri = new_uri(parms)
        print uri
        self.assertTrue(uri.startswith('http://my.vivo.edu'))


class ReadUpdateDefTestCase(unittest.TestCase):
    prefix = (
        'PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>'
        'PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>'
        'PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>'
        'PREFIX owl:   <http://www.w3.org/2002/07/owl#>'
        'PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>'
        'PREFIX bibo: <http://purl.org/ontology/bibo/>'
        'PREFIX event: <http://purl.org/NET/c4dm/event.owl#>'
        'PREFIX foaf: <http://xmlns.com/foaf/0.1/>'
        'PREFIX obo: <http://purl.obolibrary.org/obo/>'
        'PREFIX skos: <http://www.w3.org/2004/02/skos/core#>'
        'PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>'
        'PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>'
        'PREFIX vivo: <http://vivoweb.org/ontology/core#>'
    )

    def test_read_normal_def(self):
        update_def = read_update_def('data/grant_def.json', prefix=ReadUpdateDefTestCase.prefix)
        self.assertTrue(update_def.keys() == ['entity_def', 'column_defs'])

    def test_substitution(self):
        from rdflib import URIRef
        update_def = read_update_def('data/pump_def.json', prefix=ReadUpdateDefTestCase.prefix)
        self.assertTrue(update_def['entity_def']['type']) == \
            URIRef(u'http://vivoweb.org/ontology/core#Building')

    def test_invalid_def(self):
        with self.assertRaises(InvalidDefException):
            update_def = read_update_def('data/grant_invalid_def.json', prefix=ReadUpdateDefTestCase.prefix)
            print update_def

    def test_invalid_multiple_def(self):
        with self.assertRaises(InvalidDefException):
            update_def = read_update_def('data/grant_invalid_multiple_def.json', prefix=ReadUpdateDefTestCase.prefix)
            print update_def

    def test_novalue_def(self):
        with self.assertRaises(InvalidDefException):
            update_def = read_update_def('data/person_novalue_def.json', prefix=ReadUpdateDefTestCase.prefix)
            print update_def

    def test_pathlength_def(self):
        with self.assertRaises(PathLengthException):
            p = Pump('data/grant_invalidpathlength_def.json')
            n = p.get()
            print n

    def test_update_def_order(self):
        update_def = read_update_def('data/grant_def.json', prefix=ReadUpdateDefTestCase.prefix)
        self.assertEqual(update_def['entity_def']['order'][0:4], [u'deptid', u'direct_costs',
                                                                  u'cois', u'end_date'])


class MakeUpdateQueryTestCase(unittest.TestCase):
    prefix = """
PREFIX rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:     <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:      <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:      <http://www.w3.org/2002/07/owl#>
PREFIX swrl:     <http://www.w3.org/2003/11/swrl#>
PREFIX swrlb:    <http://www.w3.org/2003/11/swrlb#>
PREFIX vitro:    <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX wgs84:    <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX bibo:     <http://purl.org/ontology/bibo/>
PREFIX c4o:      <http://purl.org/spar/c4o/>
PREFIX cito:     <http://purl.org/spar/cito/>
PREFIX event:    <http://purl.org/NET/c4dm/event.owl#>
PREFIX fabio:    <http://purl.org/spar/fabio/>
PREFIX foaf:     <http://xmlns.com/foaf/0.1/>
PREFIX geo:      <http://aims.fao.org/aos/geopolitical.owl#>
PREFIX obo:      <http://purl.obolibrary.org/obo/>
PREFIX ocrer:    <http://purl.org/net/OCRe/research.owl#>
PREFIX ocresd:   <http://purl.org/net/OCRe/study_design.owl#>
PREFIX skos:     <http://www.w3.org/2004/02/skos/core#>
PREFIX uf:       <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vcard:    <http://www.w3.org/2006/vcard/ns#>
PREFIX vitro-public: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo:     <http://vivoweb.org/ontology/core#>
PREFIX scires:   <http://vivoweb.org/ontology/scientific-research#>
"""

    def test_make_query(self):
        update_def = read_update_def('data/grant_def.json', prefix=MakeUpdateQueryTestCase.prefix)
        for column_name, path in update_def['column_defs'].items():
            update_query = make_update_query(column_name, update_def['entity_def']['entity_sparql'], path)
            self.assertTrue(len(update_query) > 0)


class MakeRdfTermTestCase(unittest.TestCase):
    def test_uriref_case(self):
        from rdflib import URIRef
        input_dict = {
            "type": "uri",
            "value": "http://vivo.school.edu/individual/n531532305"
        }
        rdf_term = make_rdf_term(input_dict)
        print rdf_term
        self.assertTrue(type(rdf_term) is URIRef)


class GetGraphTestCase(unittest.TestCase):
    query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                   'username': 'vivo_root@school.edu',
                   'password': 'v;bisons',
                   'uriprefix': 'http://vivo.school.edu/individual/n',
                   'prefix':
'''
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
'''
                   }

    def test_normal_case(self):
        update_def = read_update_def('data/grant_def.json', prefix=GetGraphTestCase.query_parms['prefix'])
        a = get_graph(update_def, GetGraphTestCase.query_parms)
        print len(a)
        self.assertTrue(len(a) == 11)


class ReadCSVTestCase(unittest.TestCase):
    def test_read_csv_keys(self):
        data = read_csv("data/extension.txt", delimiter='\t')
        print data
        self.assertTrue(data.keys() == range(1, 74))

    def test_sorted_csv(self):
        data = read_csv("data/extension.txt", delimiter='\t')
        sdata = {}
        order = sorted(data, key=lambda rown: data[rown]['name'], reverse=True)
        row = 1
        for o in order:
            sdata[row] = data[o]
            row += 1
        print sdata

    def test_read_csv_minimal(self):
        data = read_csv("data/minimal.txt", delimiter='|')
        data_string = "{1: {u'overview': u'None', u'uri': u'http://vivo.school.edu/individual/n7023304'}}"
        self.assertEqual(data_string, str(data))

    def test_read_csv_fp(self):
        fp = open("data/minimal.txt", 'rU')
        data = read_csv_fp(fp, delimiter='|')
        fp.close()
        data_string = "{1: {u'overview': u'None', u'uri': u'http://vivo.school.edu/individual/n7023304'}}"
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
    query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                   'username': 'vivo_root@school.edu',
                   'password': 'v;bisons',
                   'uriprefix': 'http://vivo.school.edu/individual/n',
                   'prefix':
'''
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
'''
                   }

    def test_vivo_query(self):
        result = vivo_query("""
        SELECT ?label
        WHERE { <http://vivo.school.edu/individual/n1133> rdfs:label ?label }
        """, VIVOQueryTestCase.query_parms)
        print result
        self.assertTrue(len(result) > 0)

    def test_bad_request(self):
        from SPARQLWrapper import SPARQLExceptions
        with self.assertRaises(SPARQLExceptions.QueryBadFormed):
            result = vivo_query("""
            SEWECT ?label
            WHERE { <http://vivo.school.edu/individual/n25562> rdfs:label ?label }
            """, VIVOQueryTestCase.query_parms)
            print result


class VIVOGetTypesTestCase(unittest.TestCase):
    query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                   'username': 'vivo_root@school.edu',
                   'password': 'v;bisons',
                   'uriprefix': 'http://vivo.school.edu/individual/n',
                   'prefix':
'''
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
'''
                   }

    def test_vivo_get_types(self):
        result = get_vivo_types("?uri a foaf:Person .", VIVOGetTypesTestCase.query_parms)
        self.assertTrue(len(result) > 0)


class VIVOGetUFIDTestCase(unittest.TestCase):
    query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                   'username': 'vivo_root@school.edu',
                   'password': 'v;bisons',
                   'uriprefix': 'http://vivo.school.edu/individual/n',
                   'prefix':
'''
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
'''
                   }

    def test_vivo_get_ufid(self):
        result = get_vivo_ufid(VIVOGetUFIDTestCase.query_parms)
        self.assertTrue(len(result) > 0)


class VIVOGetAuthorsTestCase(unittest.TestCase):
    query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                   'username': 'vivo_root@school.edu',
                   'password': 'v;bisons',
                   'uriprefix': 'http://vivo.school.edu/individual/n',
                   'prefix':
'''
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
'''
                   }

    def test_vivo_get_authors(self):
        result = get_vivo_authors(VIVOGetAuthorsTestCase.query_parms)
        self.assertTrue(len(result) > 0)


class VIVOGetSponsorsTestCase(unittest.TestCase):
    query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                   'username': 'vivo_root@school.edu',
                   'password': 'v;bisons',
                   'uriprefix': 'http://vivo.school.edu/individual/n',
                   'prefix':
'''
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX ufVivo: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
'''
                   }

    def test_vivo_get_sponsorid(self):
        result = get_vivo_sponsorid(VIVOGetSponsorsTestCase.query_parms)
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

    def test_pump_serialize(self):
        p = Pump("data/pump_def.json")
        self.assertTrue(p.serialize().startswith("{\"entity_def\":"))

    def test_pump_filename(self):
        p = Pump("data/building_def.json")
        self.assertTrue("vivo:Building" in p.serialize())

    def test_pump_summarize(self):
        p = Pump("data/building_def.json")
        result = p.summarize()
        print result
        self.assertTrue("Pump Summary for data/building" in result)

    def test_pump_test(self):
        p = Pump("data/building_def.json")
        result = p.test()
        print result
        self.assertTrue("Test end" in result)

    def test_pump_get_default_filename(self):
        import os
        p = Pump("data/building_def.json")
        filename = p.out_filename
        p.get()
        self.assertTrue(os.path.isfile(filename))
        os.remove(filename)

    def test_pump_get(self):
        p = Pump("data/building_def.json")
        n_rows = p.get()
        print n_rows
        self.assertEqual(2, n_rows)

    def test_pump_update(self):
        p = Pump("data/building_def.json", verbose=True)
        p.out_filename = "data/pump_data.txt"
        [add, sub] = p.update()
        self.assertEqual(2, len(add))
        self.assertEqual(2, len(sub))


class PumpGetTestCase(unittest.TestCase):

    def test_get_no_filter(self):
        p = Pump(verbose=True)
        p.filter = False
        n_rows = p.get()
        self.assertEqual(2, n_rows)

    def test_get_filter(self):
        p = Pump("data/building_def.json")
        p.out_filename = "data/buildings_filtered.txt"
        n_rows = p.get()
        self.assertEqual(2, n_rows)

    def test_boolean_get(self):
        from vivopump import read_csv
        p = Pump("data/faculty_boolean_def.json")
        p.get()
        data = read_csv('pump_data.txt', delimiter='\t')
        nfac = 0
        for row, vals in data.items():
            if vals['faculty'] == '1':
                nfac += 1
        self.assertEqual(5, nfac)


class PumpUpdateCallTestCase(unittest.TestCase):

    def test_default_usage(self):
        p = Pump()
        self.assertTrue("pump_def.json" in p.summarize())  # Using the default definition

    def test_no_update_file(self):
        p = Pump()
        p.out_filename = 'data/no_update_file.txt'
        with self.assertRaises(IOError):
            p.update()

    def test_normal_inject(self):
        p = Pump(verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n8984374104', u'abbreviation': u'None'}}
        p.update()
        self.assertTrue("8984374104" in str(p.update_data))  # Using the injected data, not default

    def test_empty_column_defs(self):
        Pump("data/building_empty_column_def.json", verbose=True)
        self.assertTrue(True)  # No error thrown reading def

    def test_missing_uri_column_inject(self):
        p = Pump()
        p.update_data = {1: {u'overview': u'None'}}
        with self.assertRaises(KeyError):
            p.update()

    def test_inject_empty_original_graph(self):
        from rdflib import Graph, URIRef
        p = Pump()
        p.original_graph = Graph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n8984374104', u'abbreviation': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (None,
                                                 URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                                                 URIRef("http://vivoweb.org/ontology/core#Building")) in add)


class MakeRdfTermFromSourceTestCase(unittest.TestCase):
    def test_empty(self):
        from rdflib import Literal
        from vivopump import make_rdf_term_from_source

        step_def = {
            "object": {
                "literal": True,
                "datatype": "xsd:string"
            }
        }
        source_val = ''
        rdf_term = make_rdf_term_from_source(source_val, step_def)
        self.assertTrue(unicode(rdf_term) == unicode(Literal('')))

    def test_empty_compare(self):
        from rdflib import Literal
        from vivopump import make_rdf_term_from_source

        step_def = {
            "object": {
                "literal": True,
                "datatype": "xsd:string"
            }
        }
        source_val = ''
        rdf_term = make_rdf_term_from_source(source_val, step_def)
        self.assertTrue(rdf_term == Literal('', datatype="http://www.w3.org/2001/XMLSchema#string"))

    def test_lang(self):
        from rdflib import Literal
        from vivopump import make_rdf_term_from_source

        step_def = {
            "object": {
                "literal": True,
                "lang": "fr"
            }
        }
        source_val = 'a'
        rdf_term = make_rdf_term_from_source(source_val, step_def)
        self.assertTrue(rdf_term == Literal('a', lang="fr"))

    def test_ref(self):
        from rdflib import URIRef
        from vivopump import make_rdf_term_from_source

        step_def = {
            "object": {
                "literal": False
            }
        }
        source_val = 'http://any'
        rdf_term = make_rdf_term_from_source(source_val, step_def)
        self.assertTrue(rdf_term == URIRef("http://any"))

    def test_ref_string(self):
        from rdflib import URIRef
        from vivopump import make_rdf_term_from_source

        step_def = {
            "object": {
                "literal": False
            }
        }
        source_val = 'http://any'
        rdf_term = make_rdf_term_from_source(source_val, step_def)
        self.assertTrue(unicode(rdf_term) == unicode(URIRef("http://any")))


class PumpUpdateLiteralsTestCase(unittest.TestCase):

    def test_add_unicode(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph
        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n710', u'name': u'ქართული'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (URIRef("http://vivo.school.edu/individual/n710"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                                 Literal("ქართული")) in add)

    def test_change_unicode(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph
        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n711', u'name': u'বিষ্ণুপ্রিয়া মণিপুরী'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n711"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                                 Literal("বিষ্ণুপ্রিয়া মণিপুরী")) in add and
                                                (URIRef("http://vivo.school.edu/individual/n711"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                                 Literal("Ελληνικά")) in sub)

    def test_delete_unicode(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph
        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n711', u'name': u'None'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n711"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                                 Literal("Ελληνικά")) in sub)

    def test_change_with_datatype(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph
        p = Pump("data/building_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1001011525', u'abbreviation': u'PH9'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n1001011525"),
                                                 URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                                                 Literal("PH9", datatype=XSD.string)) in add)

    def test_change_with_lang(self):
        from rdflib import URIRef, Literal
        from testgraph import TestGraph
        p = Pump("data/building_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1001011525', u'name': u'Building 42'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n1001011525"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                                 Literal("Building 42", lang="en-US")) in add)

    def test_add_without_datatype(self):
        from rdflib import URIRef, Literal
        from testgraph import TestGraph
        p = Pump("data/building_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1001011525', u'url': u'http://a'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 4 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#linkURI"),
                                                 Literal("http://a")) in add)

    def test_change_without_lang(self):
        from rdflib import URIRef, Literal
        from testgraph import TestGraph
        p = Pump("data/org_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n2525', u'name': u'Ad ver tising'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n2525"),
                                                 URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                                 Literal("Ad ver tising")) in add)


class PumpUpdateTwoTestCase(unittest.TestCase):

    #   Test various scenarios of a length two path multiple predicate/single leaf

    def test_blank_to_empty(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n44',
                             u'pis': u''}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 0)

    def test_none_to_empty(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n44',
                             u'pis': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 0)

    def test_add_one_to_empty(self):
        from rdflib import URIRef
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n44',
                             u'pis': u'http://vivo.school.edu/individual/n1133'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 3 and len(sub) == 0 and (URIRef("http://vivo.school.edu/individual/n44"),
                                                 URIRef("http://vivoweb.org/ontology/core#relates"),
                                                 None) in add)

    def test_add_two_to_empty(self):
        from rdflib import URIRef
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n44',
                             u'pis': u'http://vivo.school.edu/individual/n1133;http://vivo.school.edu/individual/n3413'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 6 and len(sub) == 0 and (URIRef("http://vivo.school.edu/individual/n44"),
                                                 URIRef("http://vivoweb.org/ontology/core#relates"),
                                                 None) in add)

    def test_blank_to_two(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n45',
                             u'pis': u''}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 0)

    def test_none_to_two(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n45',
                             u'pis': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 6)

    def test_add_existing_to_two(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n45',
                             u'pis': u'http://vivo.school.edu/individual/n1133'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 3)

    def test_add_two_existing_to_two(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n45',
                             u'pis': u'http://vivo.school.edu/individual/n1133;'
                             'http://vivo.school.edu/individual/n3413'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 0)

    def test_add_one_new_to_two(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n45',
                             u'pis': u'http://vivo.school.edu/individual/n1134'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 3 and len(sub) == 6)

    def test_add_one_new_one_existing_to_two(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n45',
                             u'pis': u'http://vivo.school.edu/individual/n1133;'
                             'http://vivo.school.edu/individual/n3414'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 3 and len(sub) == 3)

    def test_add_two_new_to_two(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n45',
                             u'pis': u'http://vivo.school.edu/individual/n1134;'
                             'http://vivo.school.edu/individual/n3414'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 6 and len(sub) == 6)

    def test_add_two_new_two_existing_to_two(self):
        from testgraph import TestGraph
        p = Pump("data/grant_pi_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n45',
                             u'pis': u'http://vivo.school.edu/individual/n1133;'
                             'http://vivo.school.edu/individual/n1134;'
                             'http://vivo.school.edu/individual/n3413;'
                             'http://vivo.school.edu/individual/n3414;'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 6 and len(sub) == 0)


class PumpUpdateDataTestCase(unittest.TestCase):
    def test_unique_one_add(self):
        from rdflib import URIRef, Literal
        from testgraph import TestGraph
        p = Pump(verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n2525', u'abbreviation': u'PH9'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (URIRef("http://vivo.school.edu/individual/n2525"),
                                                 URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                                                 Literal("PH9")) in add)

    def test_unique_one_change(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph
        p = Pump(verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1001011525', u'abbreviation': u'JWR2'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and (URIRef("http://vivo.school.edu/individual/n1001011525"),
                               URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                               Literal("JWR2")) in add and
            len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n1001011525"),
                               URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                               Literal("JWRU", datatype=XSD.string)) in sub)

    def test_unique_one_delete(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph
        p = Pump(verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1001011525', u'abbreviation': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n1001011525"),
                                                 URIRef("http://vivoweb.org/ontology/core#abbreviation"),
                                                 Literal("JWRU", datatype=XSD.string)) in sub)

    def test_unique_two_add(self):
        from rdflib import URIRef
        from testgraph import TestGraph

        p = Pump("data/grant_dates_def.json", verbose=True)
        p.original_graph = TestGraph()

        # In this example, dates are enumerated

        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n44', u'start_date': u'2006'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 3 and len(sub) == 0 and (URIRef("http://vivo.school.edu/individual/n44"),
                                                 URIRef("http://vivoweb.org/ontology/core#dateTimeInterval"),
                                                 None) in add)

    def test_unique_two_change(self):
        from rdflib import URIRef
        from testgraph import TestGraph

        p = Pump("data/grant_dates_def.json", verbose=True)
        p.original_graph = TestGraph()

        # In this example, dates are enumerated

        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n125', u'end_date': u'2006'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n126"),
                                                 URIRef("http://vivoweb.org/ontology/core#end"),
                                                 None) in add and
                                                (URIRef("http://vivo.school.edu/individual/n126"),
                                                 URIRef("http://vivoweb.org/ontology/core#end"),
                                                 None) in sub)

    def test_unique_two_delete(self):
        from rdflib import URIRef
        from testgraph import TestGraph

        p = Pump("data/grant_dates_def.json", verbose=True)
        p.original_graph = TestGraph()

        # In this example, dates are enumerated

        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n125', u'end_date': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (URIRef("http://vivo.school.edu/individual/n126"),
                                                 URIRef("http://vivoweb.org/ontology/core#end"),
                                                 None) in sub)

    def test_unique_three_add_fullpath(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph

        p = Pump("data/org_def.json", verbose=True)
        p.original_graph = TestGraph()

        # Add a zip code to an org without an address, so a full path will need
        # to be created

        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n2525', u'zip': u'32653'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 5 and len(sub) == 0 and (None,
                                                 URIRef("http://www.w3.org/2006/vcard/ns#postalCode"),
                                                 Literal("32653", datatype=XSD.string)) in add)

    def test_unique_three_add_to_existing(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph

        # Add a zip code to an address already exists, the zip needs to be
        # added to the existing address

        p = Pump("data/org_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n3535', u'zip': u'32653'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 0 and (None,
                                                 URIRef("http://www.w3.org/2006/vcard/ns#postalCode"),
                                                 Literal("32653", datatype=XSD.string)) in add)

    def test_unique_three_change(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph

        # Change the zip code on an existing address

        p = Pump("data/org_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n4545', u'zip': u'32653'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (None,
                                                 URIRef("http://www.w3.org/2006/vcard/ns#postalCode"),
                                                 Literal("32653", datatype=XSD.string)) in add and
                                                (None,
                                                 URIRef("http://www.w3.org/2006/vcard/ns#postalCode"),
                                                 Literal("32604", datatype=XSD.string)) in sub)

    def test_unique_three_delete(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph

        # Delete the zip code on an existing address

        p = Pump("data/org_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n4545', u'zip': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (None,
                                                 URIRef("http://www.w3.org/2006/vcard/ns#postalCode"),
                                                 Literal("32604", datatype=XSD.string)) in sub)

    def test_unique_three_delete_not_found(self):
        from testgraph import TestGraph

        # Delete the zip code from an existing address that doesn't have a zip code.

        p = Pump("data/org_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n3535', u'zip': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)

    def test_unique_three_add(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph

        # Add a start date to a grant.  There is no date time interval, so a full path will need to be created

        p = Pump("data/grant_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n44', u'start_date': u'2015-03-01'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 5 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2015-03-01", datatype=XSD.datetime)) in add)

    def test_unique_three_add_partial_path(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph

        p = Pump("data/grant_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n55', u'start_date': u'2006-03-01'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 3 and len(sub) == 0 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2006-03-01", datatype=XSD.datetime)) in add)

    def test_unique_three_change_datetime(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph
        p = Pump("data/grant_def.json", verbose=True)
        p.original_graph = TestGraph()

        #   WARNING.  This test passes by changing the start date value on an existing datetime.
        #   Not sure if this is the desired behavior.

        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n125', u'start_date': u'2006-03-02'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 1 and len(sub) == 1 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2006-03-02", datatype=XSD.datetime)) in add and
                                                (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2010-04-01", datatype=XSD.datetime)) in sub)

    def test_unique_three_delete_datetime(self):
        from rdflib import URIRef, Literal, XSD
        from testgraph import TestGraph

        # WARNING: Delete start date value from existing datetime interval.  This may not be the desirable data
        # management action

        p = Pump("data/grant_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n125', u'start_date': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 0 and len(sub) == 1 and (None,
                                                 URIRef("http://vivoweb.org/ontology/core#dateTime"),
                                                 Literal("2010-04-01", datatype=XSD.datetime)) in sub)

    def test_multiple_one_add(self):
        from rdflib import URIRef
        from testgraph import TestGraph

        #  Add multiple values for an attribute to an entity that has no values for the attribute

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1723097935',
                               u'research_areas': u'http://vivo.school.edu/individual/n2551317090;http://vivo.school.edu/individual/n157098'}}
        p.original_graph = TestGraph()

        [add, sub] = p.update()
        self.assertTrue(
            len(add) == 2 and len(sub) == 0 and (URIRef("http://vivo.school.edu/individual/n1723097935"),
                                                 URIRef("http://vivoweb.org/ontology/core#hasResearchArea"),
                                                 URIRef("http://vivo.school.edu/individual/n2551317090")) in add and
                                                (URIRef("http://vivo.school.edu/individual/n1723097935"),
                                                 URIRef("http://vivoweb.org/ontology/core#hasResearchArea"),
                                                 URIRef("http://vivo.school.edu/individual/n157098")) in add)

    def test_multiple_one_change_nothing(self):
        from testgraph import TestGraph

        #  Do nothing if the multiple values specified match those in VIVO

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1723097935',
                             u'types': u'fac;person'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)

    def test_multiple_one_change(self):
        from testgraph import TestGraph
        from rdflib import URIRef

        #  Change the set of values adding one and removing another

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1723097935',
                             u'types': u'person;pd'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(len(add) == 1 and len(sub) == 1 and
                        (URIRef("http://vivo.school.edu/individual/n1723097935"),
                         URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                         URIRef("http://vivoweb.org/ontology/core#Postdoc")) in add and
                        (URIRef("http://vivo.school.edu/individual/n1723097935"),
                         URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                         URIRef("http://vivoweb.org/ontology/core#FacultyMember")) in sub)

    def test_multiple_one_delete(self):
        from testgraph import TestGraph

        #  Empty the set of values

        p = Pump("data/person_def.json")
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n25674',
                             u'research_areas': u'None'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 4)


class UpdateURITestCase(unittest.TestCase):
    def test_uri_not_found(self):
        from testgraph import TestGraph

        #  Use the URI when not found

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1723097936',
                             u'types': u'fac;person'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(len(add) == 2 and len(sub) == 0)

    def test_uri_is_blank(self):
        from testgraph import TestGraph

        #  Use the URI when not found

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u' ',
                             u'types': u'fac;person'}}
        p.original_graph = TestGraph()
        [add, sub] = p.update()
        self.assertTrue(len(add) == 2 and len(sub) == 0)

    def test_uri_is_invalid(self):
        from testgraph import TestGraph

        #  Use the URI when not found

        p = Pump("data/person_def.json", verbose=True)
        p.update_data = {1: {u'uri': u'not a uri',
                             u'types': u'fac;person'}}
        p.original_graph = TestGraph()

        with self.assertRaises(Exception):
            [add, sub] = p.update()
            print add, sub


class BooleanColumnTestCase(unittest.TestCase):
    def test_summarize(self):
        from testgraph import TestGraph
        p = Pump("data/person_def.json", verbose=True)
        p.original_graph = TestGraph()
        print p.update_def
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1723097935',
                             u'any1': u'1'}}
        print p.summarize()  # No exception thrown by summarize

    def test_add(self):
        from testgraph import TestGraph
        from rdflib import URIRef
        p = Pump("data/person_def.json", verbose=True)
        p.original_graph = TestGraph()
        print p.update_def
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n1723097935',
                             u'any1': u'y'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 1 and len(sub) == 0 and
                        (URIRef("http://vivo.school.edu/individual/n1723097935"),
                         URIRef("http://vivoweb.org/ontology/core#hasResearchArea"),
                         URIRef("http://any1")) in add)

    def test_remove(self):
        from testgraph import TestGraph
        from rdflib import URIRef
        p = Pump("data/person_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n25674',
                             u'any1': u'n'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 1 and
                        (URIRef("http://vivo.school.edu/individual/n25674"),
                         URIRef("http://vivoweb.org/ontology/core#hasResearchArea"),
                         URIRef("http://any1")) in sub)


class ClosureTestCase(unittest.TestCase):
    def test_read_closure(self):
        Pump("data/teaching_def.json", verbose=True)
        self.assertTrue(True)  # No exception thrown when reading a def with a closure

    def test_normal_closure(self):
        from testgraph import TestGraph
        from rdflib import URIRef
        p = Pump("data/teaching_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'',
                             u'instructor': 'http://orcid.org/0000-0002-1305-8447',
                             u'course': 'Introduction to Statistics',
                             u'start_date': '2012',
                             u'end_date': u'2013'}}
        print p.summarize()
        [add, sub] = p.update()
        self.assertTrue(len(add) == 8 and len(sub) == 0 and
                        (URIRef("http://vivo.school.edu/individual/n25674"),
                         URIRef("http://purl.obolibrary.org/obo/BFO_0000056"),
                         URIRef("http://vivo.school.edu/individual/n7501")) in add)


class PumpMergeTestCase(unittest.TestCase):
    def test_show_merge(self):
        from testgraph import TestGraph
        p = Pump("data/person_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n25674', u'action': u'b'},
                         2: {u'uri': u'http://vivo.school.edu/individual/n709', u'action': u'a1'},
                         3: {u'uri': u'http://vivo.school.edu/individual/n710', u'action': u''},
                         4: {u'uri': u'http://vivo.school.edu/individual/n1723097935', u'action': u'a1'},
                         5: {u'uri': u'http://vivo.school.edu/individual/n2084211328', u'action': u'a'},
                         6: {u'uri': u'http://vivo.school.edu/individual/n708', u'action': u'b1'},
                         7: {u'uri': u'http://vivo.school.edu/individual/n711', u'action': u'a1'},
                         }
        [add, sub] = p.update()
        self.assertTrue(len(add) == 2 and len(sub) == 6)

    def test_no_primary_merge(self):
        from testgraph import TestGraph
        p = Pump("data/person_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {3: {u'uri': u'http://vivo.school.edu/individual/n710', u'action': u''},
                         4: {u'uri': u'http://vivo.school.edu/individual/n1723097935', u'action': u'a1'},
                         7: {u'uri': u'http://vivo.school.edu/individual/n711', u'action': u'a1'},
                         }
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)

    def test_no_secondary_merge(self):
        from testgraph import TestGraph
        p = Pump("data/person_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {3: {u'uri': u'http://vivo.school.edu/individual/n710', u'action': u''},
                         4: {u'uri': u'http://vivo.school.edu/individual/n1723097935', u'action': u'a'},
                         7: {u'uri': u'http://vivo.school.edu/individual/n711', u'action': u'a'},
                         }
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)


class PumpRemoveTestCase(unittest.TestCase):
    def test_uri_not_found_case(self):
        from testgraph import TestGraph
        p = Pump("data/person_def.json")
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n20845',
                             u'action': u'remove'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)

    def test_single_uri_case(self):
        from testgraph import TestGraph
        p = Pump("data/person_def.json")
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n2084211328',
                             u'action': u'Remove'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 1)

    def test_large_case(self):
        from testgraph import TestGraph
        p = Pump("data/person_def.json", verbose=True)
        p.original_graph = TestGraph()
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n25674',
                             u'action': u'REMOVE'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 8)

    def test_not_found(self):
        from rdflib import Graph
        p = Pump("data/person_def.json")
        p.original_graph = Graph()  # empty graph
        p.update_data = {1: {u'uri': u'http://vivo.school.edu/individual/n12345678',
                             u'action': u'Remove'}}
        [add, sub] = p.update()
        self.assertTrue(len(add) == 0 and len(sub) == 0)


class PumpEnumTestCase(unittest.TestCase):
    def test_normal_case(self):
        p = Pump("data/person_def.json", verbose=True)
        summary = p.summarize()
        self.assertTrue(summary.find('people_types') > -1)


class CreateEnumTestCase(unittest.TestCase):
    query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                   'username': 'vivo_root@school.edu',
                   'password': 'v;bisons',
                   'uriprefix': 'http://vivo.school.edu/individual/n',
                   'prefix':
'''
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
'''
                   }

    def test_normal_case(self):
        from vivopump import create_enum
        import os
        filename = "data/__test_create_enum.txt"
        query = "select ?short ?vivo where {?vivo a foaf:Person . ?vivo rdfs:label ?short .} ORDER BY ?short"
        create_enum(filename, query, CreateEnumTestCase.query_parms)
        self.assertTrue(os.path.isfile(filename))
        os.remove(filename)


class PubMedTest(unittest.TestCase):

    def test_get_person_vivo_pmids(self):
        from pubmed import get_person_vivo_pmids
        query_parms = {'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                       'username': 'vivo_root@school.edu',
                       'password': 'v;bisons',
                       'uriprefix': 'http://vivo.school.edu/individual/n',
                       'prefix':
                           '''
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
PREFIX vivo: <http://vivoweb.org/ontology/core#>
                           '''
                       }
        result = get_person_vivo_pmids("http://vivo.school.edu/individual/n1133", query_parms)
        print result
        self.assertTrue(len("PMIDList") > 0)

    def test_get_catalyst_pmids(self):
        from pubmed import get_catalyst_pmids
        result = get_catalyst_pmids(first="Michael", middle="", last="Conlon", email=["mconlon@ufl.edu",
                                    "mconlon@duraspace.org"],
                                    affiliation=["%university of florida%", "%ufl.edu%"])
        print result
        self.assertTrue(len(result) > 0)

    def test_catalyst_getpmids_xml(self):
        from pubmed import catalyst_getpmids_xml
        result = catalyst_getpmids_xml(first="David", middle="R", last="Nelson", email=["nelsodr@ufl.edu"],
                                       affiliation=["%University of Florida%"])
        print result
        self.assertTrue(result.find("PMIDList") > 0)


if __name__ == "__main__":
    unittest.main()
