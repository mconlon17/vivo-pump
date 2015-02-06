#!/usr/bin/env/python
""" vivopump -- module of helper functions for the pump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "1.00"

VIVO_URI_PREFIX = "http://vivo.ufl.edu/individual/"
VIVO_QUERY_URI = "http://sparql.vivo.ufl.edu/VIVO/sparql"

import csv
import urllib
import json
import time
import string
import random


class UnicodeCsvReader(object):
    """
    From http://stackoverflow.com/questions/1846135/python-csv-
    library-with-unicode-utf-8-support-that-just-works. Added errors='ignore'
    to handle cases when the input file misrepresents itself as utf-8.
    """

    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_reader = csv.reader(f, **kwargs)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        # read and split the csv row into fields
        row = self.csv_reader.next()
        # now decode
        return [unicode(cell, self.encoding, errors='ignore') for cell in row]

    @property
    def line_num(self):
        return self.csv_reader.line_num


class UnicodeDictReader(csv.DictReader):
    def __init__(self, f, encoding="utf-8", fieldnames=None, **kwds):
        csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwds)
        self.reader = UnicodeCsvReader(f, encoding=encoding, **kwds)


def read_csv(filename, skip=True, delimiter="|"):
    """
    Given a filename, read the CSV file with that name.  We use "|" as a
    separator in CSV files to allow commas to appear in values.

    CSV files read by this function follow these conventions:
    --  use delimiter as a separator. Defaults to vertical bar.
    --  have a first row that contains column headings.  Columns headings
        must be known to VIVO, typically in the form prefix:name
    --  all elements must have values.  To specify a missing value, use
        the string "None" or "NULL" between separators, that is |None| or |NULL|
    --  leading and trailing whitespace in values is ignored.  | The  | will be
        read as "The"
    -- if skip=True, rows with too many or too few data elements are skipped.
       if Skip=False, a RowError is thrown

    CSV files processed by read_csv will be returned as a dictionary of
    dictionaries, one dictionary per row with a name of and an
    integer value for the row number of data.
    """

    class RowError(Exception):
        pass

    heading = []
    row_number = 0
    data = {}
    for row in UnicodeCsvReader(open(filename, 'rU'), delimiter=delimiter):
        i = 0
        for r in row:
            # remove white space fore and aft
            row[i] = r.strip(string.whitespace)
            i += 1
        if len(heading) == 0:
            heading = row  # the first row is the heading
            continue
        row_number += 1
        if len(row) == len(heading):
            data[row_number] = {}
            i = 0
            for r in row:
                data[row_number][heading[i]] = r
                i += 1
        elif not skip:
            raise RowError("On row " + str(row_number) + ", expecting " +
                           str(len(heading)) + " data values. Found " +
                           str(len(row)) + " data values. Row contents = " +
                           str(row))
        else:
            pass  # row has wrong number of columns and skip is True
    return data


def new_uri():
    """
    Find an unused VIVO URI with the specified VIVO_URI_PREFIX
    """
    test_uri = ""
    while True:
        test_uri = VIVO_URI_PREFIX + str(random.randint(1, 9999999999))
        query = """
            SELECT (COUNT(?z) AS ?count) WHERE {
            <""" + test_uri + """> ?y ?z
            }"""
        response = vivo_query(query)
        if int(response["results"]["bindings"][0]['count']['value']) == 0:
            break
    return test_uri


def vivo_query(query, baseurl=VIVO_QUERY_URI,
                      format="application/sparql-results+json", debug=False):
    """
    Given a SPARQL query string return result set of the SPARQL query.  Default
    is to call the UF VIVO SPARQL endpoint and receive results in JSON format
    """

    prefix = """
    PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl:   <http://www.w3.org/2002/07/owl#>
    PREFIX swrl:  <http://www.w3.org/2003/11/swrl#>
    PREFIX swrlb: <http://www.w3.org/2003/11/swrlb#>
    PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
    PREFIX bibo: <http://purl.org/ontology/bibo/>
    PREFIX c4o: <http://purl.org/spar/c4o/>
    PREFIX cito: <http://purl.org/spar/cito/>
    PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
    PREFIX fabio: <http://purl.org/spar/fabio/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX geo: <http://aims.fao.org/aos/geopolitical.owl#>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX ocrer: <http://purl.org/net/OCRe/research.owl#>
    PREFIX ocresd: <http://purl.org/net/OCRe/study_design.owl#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ufVivo: <http://vivo.ufl.edu/ontology/vivo-ufl/>
    PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
    PREFIX vitro-public: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
    PREFIX vivo: <http://vivoweb.org/ontology/core#>
    PREFIX scires: <http://vivoweb.org/ontology/scientific-research#>
    """
    params = {
        "default-graph": "",
        "should-sponge": "soft",
        "query": prefix + query,
        "debug": "on",
        "timeout": "7000",  # 7 seconds
        "format": format,
        "save": "display",
        "fname": ""
    }
    query_part = urllib.urlencode(params)
    if debug:
        print "Base URL", baseurl
        print "Query:", query_part
    start = 2.0
    retries = 10
    count = 0
    while True:
        try:
            response = urllib.urlopen(baseurl, query_part).read()
            break
        except KeyError:
            count += 1
            if count > retries:
                break
            sleep_seconds = start ** count
            print "<!-- Failed query. Count = " + str(count) + \
                  " Will sleep now for " + str(sleep_seconds) + \
                  " seconds and retry -->"
            time.sleep(sleep_seconds)  # increase the wait time with each retry
    try:
        return json.loads(response)
    except KeyError:
        return None