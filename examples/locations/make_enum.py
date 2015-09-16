#!/usr/bin/env/python

"""
    make_enum.py -- make enumerations for locations
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "0.1"

from datetime import datetime
from vivopump import get_parms, vivo_query
import codecs


def create_enum(filename, query, parms, trim=0):
    """
    Given, query, parms and a filename, execute the query and write the enum into the file
    :param: filename: name of the file to contain the enumeration
    :param: query: the query to be used to create the columns for the enumeration
    :param: parms: dictionary of VIVO SPARQL API parameters
    :param: trim:  If 0, no trim.  If k, return the first k characters as a trimmed value for short
    :return: None
    """
    data = vivo_query(query, parms)
    outfile = codecs.open(filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')
    outfile.write("short\t\vivo\n")
    for item in data['results']['bindings']:
        if trim == 0:
            outfile.write(item["short"]["value"] + "\t" + item["vivo"]["value"] + "\n")
        else:
            outfile.write(item["short"]["value"][0:trim] + "\t" + item["vivo"]["value"] + "\n")
    outfile.close()


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
          ?vivo rdf:type vivo:GeographicLocation .
          ?vivo rdfs:label ?xlabel .
    }
    GROUP BY ?vivo
    ORDER BY ?short
    """

    create_enum("location_enum.txt", query, parms)

    print datetime.now(), "End"

if __name__ == "__main__":
    main()
