#!/usr/bin/env/python

"""
    make_enum.py -- make enumerations for editorial activities
"""

from datetime import datetime
from pump.vivopump import get_parms, create_enum

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "0.1.1"


def main():
    """
    Generate the enums for editorial activities
    """
    print datetime.now(), "Start"
    parms = get_parms()

    #   person via label

    query = """
    SELECT (MIN (?xshort) AS ?short) ?vivo
    WHERE
    {
          ?vivo a foaf:Person .
          ?vivo rdfs:label ?xshort .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("person_enum.txt", query, parms)

    #   journals via label

    query = """
    SELECT (MIN (?xlabel) AS ?short) ?vivo
    WHERE
    {
          ?vivo a bibo:Journal .
          ?vivo rdfs:label ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("journal_enum.txt", query, parms)

    #   dates via datetime

    query = """
    SELECT ?short ?vivo
    WHERE
    {
          ?vivo a vivo:DateTimeValue .
          ?vivo vivo:dateTime ?short .
    }
    ORDER BY ?short
    """

    create_enum("date_enum.txt", query, parms, trim=10)

    print datetime.now(), "End"

if __name__ == "__main__":
    main()
