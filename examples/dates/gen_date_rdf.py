#!/usr/bin/env/python

"""
    gen_date_rdf.py -- generate dates for inclusion in VIVO
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from rdflib import Graph, Literal, XSD, RDF, Namespace, URIRef

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"


def make_datetime_assertions(val, prec):
    """
    Given a date value and a precision, generate the assertions for a datetime.  For
    each datetime value, three assertions are generated:

    uri a vivo:DateTimeValue
    uri vivo:dateTimePrecision prec
    uri vivo:dateTime val^"xsd:datetime"

    :param val: a datetime with the literal value to be made into assertions
    :param prec: a string containing 'y', 'ym' or 'ymd' for one of the three precisions
    :return:
    """

    uri_prefix = "http://openvivo.org/a/date"
    vivo_prefix = "http://vivoweb.org/ontology/core#"

    VIVO = Namespace(vivo_prefix)
    date_str = val.isoformat()

    if prec == 'y':
        uri = URIRef(uri_prefix + date_str[0:4])
        prec_uri = VIVO.yearPrecision
    elif prec == 'ym':
        uri = URIRef(uri_prefix + date_str[0:7])
        prec_uri = VIVO.yearMonthPrecision
    elif prec == 'ymd':
        uri = URIRef(uri_prefix + date_str[0:10])
        prec_uri = VIVO.yearMonthDayPrecision
    else:
        raise KeyError(prec)

    g.add((uri, RDF.type, VIVO.DateTimeValue))
    g.add((uri, VIVO.dateTimePrecision, prec_uri))
    g.add((uri, VIVO.dateTime, Literal(date_str, datatype=XSD.datetime)))

start_year = 2015
end_year = 2016

g = Graph()

#   Generate years

current_date = datetime(start_year, 1, 1)
end_date = datetime(end_year, 12, 31)
precision = 'y'
while current_date <= end_date:
    make_datetime_assertions(current_date, precision)
    current_date += relativedelta(years=+1)

#   Generate year month

current_date = datetime(start_year, 1, 1)
end_date = datetime(end_year, 12, 31)
precision = 'ym'
while current_date <= end_date:
    make_datetime_assertions(current_date, precision)
    current_date += relativedelta(months=+1)

#   Generate year month day

current_date = datetime(start_year, 1, 1)
end_date = datetime(end_year, 12, 31)
precision = 'ymd'
while current_date <= end_date:
    make_datetime_assertions(current_date, precision)
    current_date += relativedelta(days=+1)

#   Generate the RDF

triples_file = open('dates.rdf', 'w')
print >>triples_file, g.serialize(format='nt')
triples_file.close()
