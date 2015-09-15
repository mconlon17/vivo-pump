#!/usr/bin/env/python
# coding=utf-8
""" test_vivopump.py -- Test cases for vivopump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "1.00"

from rdflib import Graph, URIRef, Literal, RDF, RDFS


class TestGraph(Graph):
    """
    Raise this exception when update definition contains values that can not be processed
    """
    def __init__(self):
        Graph.__init__(self)
        self.add((URIRef('http://vivo.ufl.edu/individual/n25674'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n25674'), RDFS.label,
                  Literal("Doe, John")))
        self.add((URIRef('http://vivo.ufl.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#hasResearchArea'),
                  URIRef('http://any1')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#hasResearchArea'),
                  URIRef('http://any2')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#hasResearchArea'),
                  URIRef('http://any3')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n25674'),
                  URIRef('http://vivoweb.org/ontology/core#hasResearchArea'),
                  URIRef('http://any4')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n1723097935'), RDF.type,
                  URIRef('http://vivoweb.org/ontology/core#FacultyMember')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n1723097935'), RDF.type,
                  URIRef('http://vivo.ufl.edu/ontology/vivo-ufl/UFCurrentEntity')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n1723097935'), RDF.type,
                  URIRef('http://vivo.ufl.edu/ontology/vivo-ufl/UFEntity')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n1723097935'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n1412'), RDF.type,
                  URIRef('http://vivo.vivoweb.org/ontology/core#Authorship')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n1412'), URIRef('http://any'),
                  URIRef('http://vivo.ufl.edu/individual/n25674')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n2084211328'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Person')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n1001011525'), RDF.type,
                  URIRef('http://vivo.vivoweb.org/ontology/core#Building')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n1001011525'), RDFS.label,
                  Literal("Building 42")))
        self.add((URIRef('http://vivo.ufl.edu/individual/n2525'), RDF.type,
                  URIRef('http://xmlns.com/foaf/0.1/Organization')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n2525'), RDF.type,
                  URIRef('http://vivo.vivoweb.org/ontology/core#AcademicDepartment')))
        self.add((URIRef('http://vivo.ufl.edu/individual/n2525'), RDFS.label,
                  Literal("Advertising")))

    def __str__(self):
        return self.serialize(format="nt")