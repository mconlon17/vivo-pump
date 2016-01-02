#!/usr/bin/env/python
# coding=utf-8
""" test_vivopump.py -- Test cases for vivopump
"""

from rdflib import Graph, URIRef, Literal, RDF, RDFS, XSD

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "1.1.2"


class TestGraph(Graph):
    """
    Test graph for updates.  Insures starting conditions for test
    """
    def __init__(self):
        Graph.__init__(self)

        #   Person with orcid and research areas

        self.add((URIRef('http://vivo.school.edu/individual/n25674'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))
        self.add((URIRef('http://vivo.school.edu/individual/n25674'), RDFS.label,
                  Literal("Doe, John")))
        self.add((URIRef('http://vivo.school.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#orcid'),
                  Literal("http://orcid.org/0000-0002-1305-8447")))
        self.add((URIRef('http://vivo.school.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#hasResearchArea'),
                  URIRef('http://any1')))
        self.add((URIRef('http://vivo.school.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#hasResearchArea'),
                  URIRef('http://any2')))
        self.add((URIRef('http://vivo.school.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#hasResearchArea'),
                  URIRef('http://any3')))
        self.add((URIRef('http://vivo.school.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#hasResearchArea'),
                  URIRef('http://any4')))

        #   Course

        self.add((URIRef('http://vivo.school.edu/individual/n7501'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))
        self.add((URIRef('http://vivo.school.edu/individual/n7501'), RDFS.label,
                  Literal("Introduction to Statistics")))

        #   Date

        self.add((URIRef("http://vivo.school.edu/individual/n8968236376"), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#DateTimeValue')))
        self.add((URIRef("http://vivo.school.edu/individual/n8968236376"),
                  URIRef('http://vivoweb.org/ontology/core#dateTime'),
                  Literal("2012-01-01", datatype=XSD.datetime)))

        #   Another Date

        self.add((URIRef('http://vivo.school.edu/individual/n2871342684'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#DateTimeValue')))
        self.add((URIRef('http://vivo.school.edu/individual/n2871342684'),
                  URIRef('http://vivoweb.org/ontology/core#dateTime'),
                  Literal("2013-01-01", datatype=XSD.datetime)))

        #   Person with multiple types

        self.add((URIRef('http://vivo.school.edu/individual/n1723097935'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#FacultyMember')))
        self.add((URIRef('http://vivo.school.edu/individual/n1723097935'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))

        #   Authorship

        self.add((URIRef('http://vivo.school.edu/individual/n1412'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#Authorship')))
        self.add((URIRef('http://vivo.school.edu/individual/n1412'), URIRef('http://any'),
                  URIRef('http://vivo.school.edu/individual/n25674')))

        #   Person with no attributes

        self.add((URIRef('http://vivo.school.edu/individual/n2084211328'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))

        #   Person with no attributes

        self.add((URIRef('http://vivo.school.edu/individual/n708'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))

        #   Person with no attributes

        self.add((URIRef('http://vivo.school.edu/individual/n709'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))

        #   Person with no attributes

        self.add((URIRef('http://vivo.school.edu/individual/n710'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))

        #   Person with Unicode in name

        self.add((URIRef('http://vivo.school.edu/individual/n711'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))
        self.add((URIRef('http://vivo.school.edu/individual/n711'), RDFS.label,
                  Literal('Ελληνικά')))

        #   Building with name and abbreviation

        self.add((URIRef('http://vivo.school.edu/individual/n1001011525'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#Building')))
        self.add((URIRef('http://vivo.school.edu/individual/n1001011525'), RDFS.label,
                  Literal("Building 42")))
        self.add((URIRef('http://vivo.school.edu/individual/n1001011525'),
                  URIRef('http://vivoweb.org/ontology/core#abbreviation'),
                  Literal("JWRU", datatype=XSD.string)))

        #   org no address

        self.add((URIRef('http://vivo.school.edu/individual/n2525'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Organization')))
        self.add((URIRef('http://vivo.school.edu/individual/n2525'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#AcademicDepartment')))
        self.add((URIRef('http://vivo.school.edu/individual/n2525'), RDFS.label,
                  Literal("Advertising")))

        #   org with address, no zip code

        self.add((URIRef('http://vivo.school.edu/individual/n3535'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Organization')))
        self.add((URIRef('http://vivo.school.edu/individual/n3535'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#AcademicDepartment')))
        self.add((URIRef('http://vivo.school.edu/individual/n3535'), RDFS.label,
                  Literal("Physics")))
        self.add((URIRef('http://vivo.school.edu/individual/n3535'),
                  URIRef('http://purl.obolibrary.org/obo/ARG_2000028'),
                  URIRef('http://vivo.school.edu/individual/n80')))
        self.add((URIRef('http://vivo.school.edu/individual/n80'), RDF.type,  # a vcard
                  URIRef('http://www.w3.org/2006/vcard/ns#Kind')))
        self.add((URIRef('http://vivo.school.edu/individual/n80'),
                  URIRef('http://www.w3.org/2006/vcard/ns#hasAddress'),
                  URIRef('http://vivo.school.edu/individual/n801')))
        self.add((URIRef('http://vivo.school.edu/individual/n801'), RDF.type,  # an address
                  URIRef('http://www.w3.org/2006/vcard/ns#Address')))
        self.add((URIRef('http://vivo.school.edu/individual/n801'),
                  URIRef('http://www.w3.org/2006/vcard/ns#country'),
                  Literal("US", datatype=XSD.string)))
        self.add((URIRef('http://vivo.school.edu/individual/n801'),
                  URIRef('http://www.w3.org/2006/vcard/ns#locality'),
                  Literal("Gainesville", datatype=XSD.string)))
        self.add((URIRef('http://vivo.school.edu/individual/n801'),
                  URIRef('http://www.w3.org/2006/vcard/ns#region'),
                  Literal("FL", datatype=XSD.string)))
        self.add((URIRef('http://vivo.school.edu/individual/n801'),
                  URIRef('http://www.w3.org/2006/vcard/ns#streetAddress'),
                  Literal("3600 Mowry Road; Mail stop 6", datatype=XSD.string)))

        #   org with complete address

        self.add((URIRef('http://vivo.school.edu/individual/n4545'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Organization')))
        self.add((URIRef('http://vivo.school.edu/individual/n4545'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#AcademicDepartment')))
        self.add((URIRef('http://vivo.school.edu/individual/n4545'), RDFS.label,
                  Literal("Pediatrics")))
        self.add((URIRef('http://vivo.school.edu/individual/n4545'),
                  URIRef('http://purl.obolibrary.org/obo/ARG_2000028'),
                  URIRef('http://vivo.school.edu/individual/n90')))
        self.add((URIRef('http://vivo.school.edu/individual/n90'), RDF.type,  # a vcard
                  URIRef('http://www.w3.org/2006/vcard/ns#Kind')))
        self.add((URIRef('http://vivo.school.edu/individual/n90'),
                  URIRef('http://www.w3.org/2006/vcard/ns#hasAddress'),
                  URIRef('http://vivo.school.edu/individual/n901')))
        self.add((URIRef('http://vivo.school.edu/individual/n901'), RDF.type,  # an address
                  URIRef('http://www.w3.org/2006/vcard/ns#Address')))
        self.add((URIRef('http://vivo.school.edu/individual/n901'),
                  URIRef('http://www.w3.org/2006/vcard/ns#country'),
                  Literal("US", datatype=XSD.string)))
        self.add((URIRef('http://vivo.school.edu/individual/n901'),
                  URIRef('http://www.w3.org/2006/vcard/ns#locality'),
                  Literal("Gainesville", datatype=XSD.string)))
        self.add((URIRef('http://vivo.school.edu/individual/n901'),
                  URIRef('http://www.w3.org/2006/vcard/ns#region'),
                  Literal("FL", datatype=XSD.string)))
        self.add((URIRef('http://vivo.school.edu/individual/n901'),
                  URIRef('http://www.w3.org/2006/vcard/ns#streetAddress'),
                  Literal("3600 Mowry Road; Mail stop 4", datatype=XSD.string)))
        self.add((URIRef('http://vivo.school.edu/individual/n901'),
                  URIRef('http://www.w3.org/2006/vcard/ns#postalCode'),
                  Literal("32604", datatype=XSD.string)))

        #   grant with no datetime interval and no principal investigators

        self.add((URIRef('http://vivo.school.edu/individual/n44'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#Grant')))
        self.add((URIRef('http://vivo.school.edu/individual/n44'), RDFS.label,
                  Literal("Field trial of CHX1234 v PPC45")))

        #   grant with two investigators

        self.add((URIRef('http://vivo.school.edu/individual/n45'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#Grant')))
        self.add((URIRef('http://vivo.school.edu/individual/n45'), RDFS.label,
                  Literal("Investigator Trial")))

        self.add((URIRef('http://vivo.school.edu/individual/n45'),
                  URIRef('http://vivoweb.org/ontology/core#relates'),
                  URIRef('http://vivo.school.edu/individual/n46')))
        self.add((URIRef('http://vivo.school.edu/individual/n46'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#PrincipalInvestigatorRole')))
        self.add((URIRef('http://vivo.school.edu/individual/n46'),
                  URIRef('http://purl.obolibrary.org/obo/RO_0000052'),  # inheres in
                  URIRef('http://vivo.school.edu/individual/n1133')))  # investigator URI

        self.add((URIRef('http://vivo.school.edu/individual/n45'),
                  URIRef('http://vivoweb.org/ontology/core#relates'),
                  URIRef('http://vivo.school.edu/individual/n47')))
        self.add((URIRef('http://vivo.school.edu/individual/n47'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#PrincipalInvestigatorRole')))
        self.add((URIRef('http://vivo.school.edu/individual/n47'),
                  URIRef('http://purl.obolibrary.org/obo/RO_0000052'),  # inheres in
                  URIRef('http://vivo.school.edu/individual/n3413')))  # investigator URI

        #   grant with partial datetime interval (end, no start)

        self.add((URIRef('http://vivo.school.edu/individual/n55'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#Grant')))
        self.add((URIRef('http://vivo.school.edu/individual/n55'), RDFS.label,
                  Literal("Influences on French Opera 1890-1893")))
        self.add((URIRef('http://vivo.school.edu/individual/n55'),
                  URIRef('http://vivoweb.org/ontology/core#dateTimeInterval'),
                  URIRef('http://vivo.school.edu/individual/n123')))
        self.add((URIRef('http://vivo.school.edu/individual/n123'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#DateTimeInterval')))
        self.add((URIRef('http://vivo.school.edu/individual/n123'),
                  URIRef('http://vivoweb.org/ontology/core#end'),
                  URIRef('http://vivo.school.edu/individual/n124')))
        self.add((URIRef('http://vivo.school.edu/individual/n124'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#DateTimeValue')))
        self.add((URIRef('http://vivo.school.edu/individual/n124'),
                  URIRef('http://vivoweb.org/ontology/core#dateTime'),
                  Literal("2015-12-31", datatype=XSD.datetime)))

        #   grant with full datetime interval

        self.add((URIRef('http://vivo.school.edu/individual/n125'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#Grant')))
        self.add((URIRef('http://vivo.school.edu/individual/n125'), RDFS.label,
                  Literal("Influences on French Opera 1890-1893")))
        self.add((URIRef('http://vivo.school.edu/individual/n125'),
                  URIRef('http://vivoweb.org/ontology/core#dateTimeInterval'),
                  URIRef('http://vivo.school.edu/individual/n126')))
        self.add((URIRef('http://vivo.school.edu/individual/n126'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#DateTimeInterval')))
        self.add((URIRef('http://vivo.school.edu/individual/n126'),
                  URIRef('http://vivoweb.org/ontology/core#start'),
                  URIRef('http://vivo.school.edu/individual/n127')))
        self.add((URIRef('http://vivo.school.edu/individual/n127'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#DateTimeValue')))
        self.add((URIRef('http://vivo.school.edu/individual/n127'),
                  URIRef('http://vivoweb.org/ontology/core#dateTime'),
                  Literal("2010-04-01", datatype=XSD.datetime)))
        self.add((URIRef('http://vivo.school.edu/individual/n126'),
                  URIRef('http://vivoweb.org/ontology/core#end'),
                  URIRef('http://vivo.school.edu/individual/n128')))
        self.add((URIRef('http://vivo.school.edu/individual/n128'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#DateTimeValue')))
        self.add((URIRef('http://vivo.school.edu/individual/n128'),
                  URIRef('http://vivoweb.org/ontology/core#dateTime'),
                  Literal("2014-03-31", datatype=XSD.datetime)))

    def __str__(self):
        return self.serialize(format="nt")
