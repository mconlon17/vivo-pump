#!/usr/bin/env/python

"""
    make_enum.py -- make enumerations for grants
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "0.1.2"

from datetime import datetime
from vivopump import get_parms, create_enum


def main():
    """
    Generate the enums for grants
    """
    print datetime.now(), "Start"
    parms = get_parms()

    #   person

    query = """
    SELECT (MIN (?xlabel) AS ?short) ?vivo
    WHERE
    {
          ?vivo vivo:orcid ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("orcid_enum.txt", query, parms)

    #   department

    query = """
    SELECT (MIN (?xlabel) AS ?short) ?vivo
    WHERE
    {
          ?vivo a vivo:Department .
          ?vivo rdfs:label ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("dept_enum.txt", query, parms)

    print datetime.now(), "End"

if __name__ == "__main__":
    main()
