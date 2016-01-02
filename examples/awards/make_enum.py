#!/usr/bin/env/python

"""
    make_enum.py -- make enumerations for adding awards
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "0.1.2"

from datetime import datetime

from pump.vivopump import get_parms, create_enum


def main():
    """
    Generate the enums for awards
    """
    print datetime.now(), "Start"
    parms = get_parms()

    #   person

    query = """
    SELECT ?short ?vivo
    WHERE {
      ?vivo a foaf:Person .
      ?vivo rdfs:label ?short .
    }
    ORDER BY ?short
    """

    create_enum("person_enum.txt", query, parms)

    #   school

    query = """
    SELECT ?short ?vivo
    WHERE {
      ?vivo a foaf:Organization .
      ?vivo rdfs:label ?short .
    }
    ORDER BY ?short
    """

    create_enum("org_enum.txt", query, parms)

    #   date

    query = """
    SELECT ?short ?vivo
    WHERE {
      ?vivo a vivo:DateTimeValue .
      ?vivo vivo:dateTimePrecision vivo:yearPrecision .
      ?vivo vivo:dateTime ?short .
    }
    ORDER BY ?short
    """

    create_enum("date_enum.txt", query, parms, trim=4)

    #   academic degree

    query = """
    SELECT ?short ?vivo
    WHERE {
      ?vivo a vivo:Award .
      ?vivo rdfs:label ?short .
    }
    ORDER BY ?short
    """

    create_enum("award_enum.txt", query, parms)

    print datetime.now(), "End"
    return None


if __name__ == "__main__":
    main()
