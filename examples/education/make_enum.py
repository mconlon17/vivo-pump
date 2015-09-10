#!/usr/bin/env/python

"""
    make_enum.py -- make enumerations for adding degrees
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from datetime import datetime
from vivopump import get_parms, vivo_query


def create_enum(filename, query, parms, trim=0):
    """
    Given, query, parms and a filename, execute the query and write the enum into the file
    :param: filename:
    :param: query:
    :param: parms:
    :param: trim:
    :return: None
    """
    data = vivo_query(query, parms)
    with open(filename, "w") as f:
        print >>f, "short\tvivo"
        for item in data['results']['bindings']:
            if trim == 0:
                print >>f, item["short"]["value"] + "\t" + item["vivo"]["value"]
            else:
                print >>f, item["short"]["value"][0:trim] + "\t" + item["vivo"]["value"]


def main():
    """
    Generate the enums for degrees
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
      ?vivo a vivo:University .
      ?vivo rdfs:label ?short .
    }
    ORDER BY ?short
    """

    create_enum("school_enum.txt", query, parms)

    #   date

    query = """
    SELECT ?short ?vivo
    WHERE {
      ?vivo a vivo:DateTimeValue .
      ?vivo vivo:dateTimePrecision vivo:yearMonthPrecision .
      ?vivo vivo:dateTime ?short .
    }
    ORDER BY ?short
    """

    create_enum("date_enum.txt", query, parms, trim=7)

    #   academic degree

    query = """
    SELECT ?short ?vivo
    WHERE {
      ?vivo a vivo:AcademicDegree .
      ?vivo rdfs:label ?short .
    }
    ORDER BY ?short
    """

    create_enum("degree_enum.txt", query, parms)

    print datetime.now(), "End"
    return None


if __name__ == "__main__":
    main()
