#!/usr/bin/env/python

"""
    make_enum.py -- make enumerations for orgs
"""

from datetime import datetime

from pump.vivopump import get_parms, create_enum

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2017 (c) Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "0.2"


def main():
    """
    Generate the organization enum
    """
    print datetime.now(), "Start"
    parms = get_parms()

    #   Organization

    query = """
    SELECT (MIN (?xlabel) AS ?short) ?vivo
    WHERE
    {
          ?vivo rdf:type foaf:Organization .
          ?vivo rdfs:label ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("country_enum.txt", query, parms)

    #   Country

    query = """
    SELECT (MIN (?xlabel) AS ?short) ?vivo
    WHERE
    {
          ?vivo rdf:type vivo:Country .
          ?vivo rdfs:label ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("country_enum.txt", query, parms)

    print datetime.now(), "End"

if __name__ == "__main__":
    main()
