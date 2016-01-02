#!/usr/bin/env/python

"""
    make_enum.py -- make enumerations for education
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "0.1.2"

from datetime import datetime

from pump.vivopump import get_parms, create_enum


def main():
    """
    Generate the enums for degrees
    """
    print datetime.now(), "Start"
    parms = get_parms()

    #   person

    query = """
    SELECT (MIN (?xlabel) AS ?short) ?vivo
    WHERE
    {
          ?vivo a foaf:Person .
          ?vivo rdfs:label ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("person_enum.txt", query, parms)

    #   degree

    query = """
    SELECT (MIN (?xlabel) AS ?short) ?vivo
    WHERE
    {
          ?vivo a vivo:AcademicDegree .
          ?vivo rdfs:label ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("degree_enum.txt", query, parms)

    #   school

    query = """
    SELECT (MIN (?xlabel) AS ?short) ?vivo
    WHERE
    {
          ?vivo a vivo:University .
          ?vivo rdfs:label ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("school_enum.txt", query, parms)

    #   dates

    query = """
    SELECT ?short ?vivo
    WHERE
    {
          ?vivo a vivo:DateTimeValue .
          ?vivo vivo:dateTimePrecision vivo:yearMonthPrecision .
          ?vivo vivo:dateTime ?short .
    }
    ORDER BY ?short
    """

    create_enum("date_enum.txt", query, parms, trim=7)

    print datetime.now(), "End"

if __name__ == "__main__":
    main()
