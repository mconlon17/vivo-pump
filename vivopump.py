#!/usr/bin/env/python
""" vivopump -- module of helper functions for the pump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2015 Michael Conlon"
__license__ = "BSD 3-Clause license"
__version__ = "1.01"

import csv
import string
import random


class InvalidDataException(Exception):
    """
    Raise this exception when update data contains values that can not be processed
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


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
        """
        Read and split the csv row into fields
        """
        row = self.csv_reader.next()
        # now decode
        return [unicode(cell, self.encoding, errors='ignore') for cell in row]

    @property
    def line_num(self):
        """
        Return line number
        """
        return self.csv_reader.line_num


class UnicodeDictReader(csv.DictReader):
    """
    A Unicode CSV Reader
    """
    def __init__(self, f, encoding="utf-8", fieldnames=None, **kwds):
        csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwds)
        self.reader = UnicodeCsvReader(f, encoding=encoding, **kwds)


def read_csv(filename, skip=True, delimiter='|'):
    """
    Read a CSV file, return dictionary object
    :param filename: name of file to read
    :param skip: should lines with invalid number of columns be skipped?  False=Throw Exception
    :param delimiter: The delimiter for CSV files
    :return: Dictionary object
    """
    fp = open(filename, 'rU')
    data = read_csv_fp(fp, skip, delimiter)
    fp.close()
    return data


def read_csv_fp(fp, skip=True, delimiter="|"):
    """
    Given a filename, read the CSV file with that name.  We use "|" as a
    separator in CSV files to allow commas to appear in values.

    CSV files read by this function follow these conventions:
    --  use delimiter as a separator. Defaults to vertical bar.
    --  have a first row that contains column headings.
    --  all elements must have values.  To specify a missing value, use
        the string "None" or "NULL" between separators, that is |None| or |NULL|
    --  leading and trailing whitespace in values is ignored.  | The  | will be
        read as "The"
    -- if skip=True, rows with too many or too few data elements are skipped.
       if skip=False, a RowError is thrown

    CSV files processed by read_csv will be returned as a dictionary of
    dictionaries, one dictionary per row keyed by an integer row number.  This supports
    maintaining the order of the data input, which is important for some applications
    """

    class RowError(Exception):
        """
        Thrown when the number of data elements on a row in a CSV is not equal to the number of header elements
        """
        pass

    heading = []
    row_number = 0
    data = {}
    for row in UnicodeCsvReader(fp, delimiter=delimiter):
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


def write_csv_fp(fp, data, delimiter='|'):
    """
    Write a CSV to a file pointer.  Used to support stdout.
    :param fp: File pointer.  Could be stdout.
    :param data: data to be written
    :param delimiter: field delimiter for output
    :return:
    """
    var_names = data[data.keys()[1]].keys()  # create a list of var_names from the first row
    fp.write(delimiter.join(var_names) + '\n')
    for key in sorted(data.keys()):
        fp.write(delimiter.join([data[key][x] for x in var_names]) + '\n')


def write_csv(filename, data, delimiter='|'):
    """
    Given a filename, a data structure as produced by read_csv and an optional delimiter, write a file
    that can be read by read_csv

    The data structure is a dictionary keyed by an integer of "row numbers" preserving the natural
    order of the data.  Each element is in turn a dictionary of name value pairs.  All values are
    strings

    :param filename: name of file to write
    :param data: data structure to be written to the file
    :param delimiter: field delimiter.  Popular choices are '|', '\t' and ','
    :return:
    """
    with open(filename, 'w') as f:
        f.write(delimiter.join(data[data.keys()[1]].keys()) + '\n')
        for key in sorted(data.keys()):
            f.write(delimiter.join(data[key].values()) + '\n')


def replace_initials(s):
    """
    For a string s, find all occurrences of A. B. etc and replace them with A B etc
    :param s:
    :return: string with replacements made
    """
    import re

    def repl_function(m):
        """
        Helper function for re.sub
        """
        return m.group(0)[0]

    t = re.sub('[A-Z]\.', repl_function, s)
    return t


def key_string(s):
    """
    Given a string s, return a string with a bunch of punctuation and special
    characters removed and then everything lower cased.  Useful for matching
    strings in which case, punctuation and special characters should not be
    considered in the match
    """
    k = s.encode("utf-8", "ignore").translate(None,
                                              """ \t\n\r\f!@#$%^&*()_+:"<>?-=[]\\;'`~,./""")
    k = k.lower()
    return k


def get_vivo_types(selector, separator=';'):
    """
    Query VIVO using the selector and return a dictionary with keys of all uri satisfying the selector and
    data of all the types for each uri, separated by the separator
    :return: dictionary of types keyed by uri
    """
    query = """
    select ?uri (GROUP_CONCAT(?type; separator="{{separator}}") AS ?types)
    where {
      {{selector}}
      ?uri rdf:type ?type .}
    GROUP BY ?uri
    """
    q = query.replace("{{separator}}", separator)
    q = q.replace("{{selector}}", selector)
    a = vivo_query(q)
    types = [x['types']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(uri, types))


def get_vivo_ufid():
    """
    Query VIVO and return a list of all the ufid found in VIVO
    :return: dictionary of uri keyed by ufid
    """
    query = "select ?uri ?ufid where {?uri uf:ufid ?ufid .}"
    a = vivo_query(query)
    ufid = [x['ufid']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(ufid, uri))


def get_vivo_publishers():
    """
    Query VIVO and return a list of all the publishers found in VIVO
    :return: dictionary of uri keyed by simplified publisher name
    """
    query = "select ?uri ?label where {?uri a vivo:Publisher . ?uri rdfs:label ?label .}"
    a = vivo_query(query)
    label = [key_string(x['label']['value']) for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(label, uri))


def get_vivo_journals():
    """
    Query VIVO and return a list of all the journals found in VIVO
    :return: dictionary of uri keyed by ISSN
    """
    query = "select ?uri ?issn where {?uri bibo:issn ?issn .}"
    a = vivo_query(query)
    issn = [x['issn']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(issn, uri))


def get_vivo_ccn():
    """
    Query VIVO and return a list of all the ccn found in VIVO
    :return: dictionary of uri keyed by ccn
    """
    query = "select ?uri ?ccn where {?uri uf:ccn ?ccn .}"
    a = vivo_query(query)
    ccn = [x['ccn']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(ccn, uri))


def get_vivo_sponsorid():
    """
    Query VIVO and return a list of all the sponsorid found in VIVO
    :return: dictionary of uri keyed by sponsorid
    """
    query = "select ?uri ?sponsorid where {?uri uf:sponsorid ?sponsorid .}"
    a = vivo_query(query)
    sponsorid = [x['sponsorid']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(sponsorid, uri))


def get_vivo_authors():
    """
    Query VIVO and return a list of all the authors found in VIVO.  Authors are people connected to
    publications through authorships
    :return: dictionary of author uri keyed by display_name (that won't work!)
    """
    query = """
    SELECT ?uri ?display_name
    WHERE
    {
        ?art a bibo:AcademicArticle .
        ?art bibo:doi ?doi .
        ?art vivo:relatedBy ?a .
        ?a a vivo:Authorship .
        ?a vivo:relates ?author .
        ?uri a foaf:Person .
        ?uri rdfs:label ?display_name .
    }
    """
    a = vivo_query(query)
    display_name = [x['display_name']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(display_name, uri))


def get_vivo_positions():
    """
    Query VIVO and return a list of all the UF positions found in VIVO.  UF positions will
    have an hrTitle.  Non UF positions will not have this property
    :return: dictionary of position uri keyed by ufid, deptid, hr_title, start_date
    """
    query = """
    select ?uri ?ufid ?deptid ?hr_title ?start_date
    where {
      ?uri a vivo:Position .
      ?uri vivo:relates ?x . ?x uf:ufid ?ufid .
      ?uri vivo:relates ?y . ?y uf:deptid ?deptid .
      ?uri uf:hrTitle ?hr_title .
      ?uri vivo:dateTimeInterval ?dti . ?dti vivo:start ?start . ?start vivo:dateTimeValue ?start_date .
    }
    """
    a = vivo_query(query)
    ufids = [x['ufid']['value'] for x in a['results']['bindings']]
    deptids = [x['deptid']['value'] for x in a['results']['bindings']]
    hr_titles = [x['hr_title']['value'] for x in a['results']['bindings']]
    start_dates = [x['start_date']['value'] for x in a['results']['bindings']]
    keys = [';'.join(x) for x in zip(ufids, deptids, hr_titles, start_dates)]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(keys, uri))


def read_update_def(filename):
    """
    Read an update_def in JSON format, from a file
    :param filename: name of file to read
    :rtype: dict
    :return: JSON-like object from file, replacing all URI strings with URIRef objects
    """

    def cast_to_rdflib(t):
        """
        Given a string t containing the name of an rdflib object, return the rdflib object.  For now
        this is returns xsd data types

        Will throw a KeyValue error if t is not a known data type

        :param t:
        :return: an xsd data type
        """
        from rdflib import XSD
        cast_table = {
            'xsd:integer': XSD.integer,
            'xsd:string': XSD.string,
            'xsd:datetime': XSD.datetime,
            'xsd:boolean': XSD.boolean,
            'xsd:decimal': XSD.decimal,
            'xsd:anyURI': XSD.anyURI
        }
        r = cast_table[t]
        return r

    def fixit(current_object):
        """
        Read the def data structure and replace all string URIs with URIRef entities
        :param current_object: the piece of the data structure to be fixed
        :return current_object: the piece repaired in place
        """
        from rdflib import URIRef
        if isinstance(current_object, dict):
            for k in current_object.keys():
                current_object[k] = fixit(current_object[k])
        elif isinstance(current_object, list):
            for i in range(0, len(current_object)):
                current_object[i] = fixit(current_object[i])
        elif isinstance(current_object, basestring):
            if current_object.startswith("http://"):
                current_object = URIRef(current_object)
            elif current_object.startswith("xsd:"):
                current_object = cast_to_rdflib(current_object)
        return current_object

    def add_order(a, b):
        """
        :param a: update_def
        :param b: string of input file
        :return a new update_def dictionary with an order list in the entity def
        """
        defn = a
        loc = []
        var_list = []
        for var in defn['column_defs'].keys():
            var_list.append(var)
            loc.append(b.find(var + '":'))
        seq = sorted(loc)
        order = [var_list[seq.index(v)] for v in loc]
        defn['entity_def']['order'] = order
        return defn

    import json
    with open(filename, "r") as my_file:
        data = my_file.read()
        update_def = fixit(json.loads(data))
        update_def = add_order(update_def, data)
    return update_def


def add_qualifiers(input_path):
    """
    Given an update_def input_path, generate the SPARQL fragment to express the qualifiers in the path, if any
    :param input_path:
    :return:
    """
    return ' '.join([x['object'].get('qualifier', '') for x in input_path])


def make_update_query(entity_sparql, path):
    """
    Given a path from an update_def data structure, generate the query needed to pull the triples from VIVO that might
    be updated.  Here's what the queries look like by path length

    Path length 1 example:

            select ?uri (vivo:subOrganizationWithin as ?p) ?o
            where {
                ... entity sparql goes here ...
                ?uri vivo:subOrganizationWithin ?o
            }

    Path Length 2 example:

            select ?uri (vivo:webpage as ?p) (?webpage as ?o) (vivo:linkURI as ?p2) ?o2
            where {
                ... entity sparql goes here ...
                ?uri vivo:webpage ?webpage . ?webpage vivo:linkURI ?o2 .
            }

    Path length 3 example:

            select ?uri (vivo:dateTimeInterval as ?p) (?award_period as ?o) (vivo:end as ?p2)
                                                            (?end as ?o2) (vivo:dateTime as ?p3) ?o3
            where {
                ... entity sparql goes here ...
                ?uri vivo:dateTimeInterval ?award_period . ?award_period vivo:end ?end . ?end vivo:dateTime ?o3 .
            }

    :return: a sparql query string
    """
    query = ""
    if len(path) == 1:
        query = 'select ?uri (<' + str(path[0]['predicate']['ref']) + '> as ?p) ?o\n' + \
                '    where { ' + entity_sparql + '\n    ?uri <' + str(path[0]['predicate']['ref']) + '> ?o' + \
                ' . ' + add_qualifiers(path) + ' \n}'
    elif len(path) == 2:
        query = 'select ?uri (<' + str(path[0]['predicate']['ref']) + '> as ?p) ' + \
                '(?' + path[0]['object']['name'] + ' as ?o) (<' + \
                str(path[1]['predicate']['ref']) + '> as ?p2) ?o2\n' + \
                '    where { ' + entity_sparql + '\n    ?uri <' + str(path[0]['predicate']['ref']) + '> ?' + \
                path[0]['object']['name'] + ' . ?' + \
                path[0]['object']['name'] + ' <' + str(path[1]['predicate']['ref']) + '> ?o2' + \
                ' . ' + add_qualifiers(path) + ' \n}'
    elif len(path) == 3:
        query = 'select ?uri (<' + str(path[0]['predicate']['ref']) + '> as ?p) ' + \
                '(?' + path[0]['object']['name'] + ' as ?o) (<' + str(path[1]['predicate']['ref']) + '> as ?p2) (?' + \
                path[1]['object']['name'] + ' as ?o2) (<' + str(path[2]['predicate']['ref']) + '> as ?p3) ?o3\n' + \
                'where { ' + entity_sparql + '\n    ?uri <' + str(path[0]['predicate']['ref']) + '> ?' + \
                path[0]['object']['name'] + ' . ?' + \
                path[0]['object']['name'] + ' <' + str(path[1]['predicate']['ref']) + '> ?' + \
                path[1]['object']['name'] + \
                ' . ?' + path[1]['object']['name'] + ' <' + str(path[2]['predicate']['ref']) + '> ?o3' + \
                ' . ' + add_qualifiers(path) + ' \n}'
    return query


def make_rdf_term(row_term):
    """
    Given a row term from a JSON object returned by a SPARQL query (whew!) return a corresponding
    rdflib term -- either a Literal or a URIRef
    :param row_term:
    :return: an rdf_term, either Literal or URIRef
    """
    from rdflib import Literal, URIRef

    if row_term['type'] == 'literal' or row_term['type'] == 'typed-literal':
        rdf_term = Literal(row_term['value'], datatype=row_term.get('datatype', None),
                           lang=row_term.get('xml:lang', None))
    else:
        rdf_term = URIRef(row_term['value'])
    return rdf_term


def get_graph(update_def, debug=False):
    """
    Given the update def, get a graph from VIVO of the triples eligible for updating
    :return: graph of triples
    """

    from rdflib import Graph, URIRef

    a = Graph()
    entity_query = 'select ?uri (<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> as ?p) (<' + \
        str(update_def['entity_def']['type']) + '> as ?o)\nwhere {\n    ' + \
        update_def['entity_def']['entity_sparql'] + '\n}'
    result = vivo_query(entity_query, debug=debug)
    for row in result['results']['bindings']:
        s = URIRef(row['uri']['value'])
        p = URIRef(row['p']['value'])
        o = make_rdf_term(row['o'])
        a.add((s, p, o))
    for path in update_def['column_defs'].values():
        update_query = make_update_query(update_def['entity_def']['entity_sparql'], path)
        if len(update_query) == 0:
            continue
        result = vivo_query(update_query, debug=debug)
        for row in result['results']['bindings']:
            s = URIRef(row['uri']['value'])
            p = URIRef(row['p']['value'])
            o = make_rdf_term(row['o'])
            a.add((s, p, o))
            if 'p2' in row and 'o2' in row:
                p2 = URIRef(row['p2']['value'])
                o2 = make_rdf_term(row['o2'])
                a.add((o, p2, o2))
                if 'p3' in row and 'o3' in row:
                    p3 = URIRef(row['p3']['value'])
                    o3 = make_rdf_term(row['o3'])
                    a.add((o2, p3, o3))
        if debug:
            print "Triples in original graph", len(a)
    return a


def new_uri(uri_prefix='http://vivo.school.edu/individual/'):
    """
    Find an unused VIVO URI with the specified VIVO_URI_PREFIX
    """
    test_uri = ""
    while True:
        test_uri = uri_prefix + str(random.randint(1, 9999999999))
        query = """
            SELECT (COUNT(?z) AS ?count) WHERE {
            <""" + test_uri + """> ?y ?z
            }"""
        response = vivo_query(query)
        if int(response["results"]["bindings"][0]['count']['value']) == 0:
            break
    return test_uri


def vivo_query(query, parms={'query_uri': 'http://localhost:8080/vivo/api/sparqlQuery',
                             'username': 'vivo_root@school.edu', 'password': 'v;bisons'}, debug=False):
    """
    A new VIVO query function using SparqlWrapper.  Tested with Stardog, UF VIVO and Dbpedia
    :param query: SPARQL query.  VIVO PREFIX will be added
    :param debug: boolean. If true, query will be printed to stdout
    :return: result object, typically JSON
    :rtype: dict
    """
    prefix = """
    PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl:   <http://www.w3.org/2002/07/owl#>
    PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
    PREFIX bibo: <http://purl.org/ontology/bibo/>
    PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
    PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
    PREFIX vivo: <http://vivoweb.org/ontology/core#>
    """
    from SPARQLWrapper import SPARQLWrapper, JSON
    if debug:
        print "In vivo_query"
        print parms['query_uri']
        print query
    sparql = SPARQLWrapper(parms['query_uri'])
    new_query = prefix + query
    sparql.setQuery(new_query)
    if debug:
        print "after setQuery"
        print new_query
    sparql.setReturnFormat(JSON)
    sparql.addParameter("email", parms['username'])
    sparql.addParameter("password", parms['password'])
    # sparql.setCredentials(parms['username'], parms['password'])
    results = sparql.query()
    results = results.convert()
    return results


def write_update_def(update_def, filename):
    """
    Write update_def to a json_file
    :param filename: name of file to write
    :return: None.  A file is written
    """
    import json
    out_file = open(filename, "w")
    json.dump(update_def, out_file, indent=4)
    out_file.close()
    return


def improve_email(email):
    """
    Given an email string, fix it
    """
    import re
    exp = re.compile(r'\w+\.*\w+@\w+\.(\w+\.*)*\w+')
    s = exp.search(email)
    if s is None:
        return ""
    elif s.group() is not None:
        return s.group()
    else:
        return ""


def improve_phone_number(phone, debug=False):
    """
    Given an arbitrary string that attempts to represent a phone number,
    return a best attempt to format the phone number according to ITU standards

    If the phone number can not be repaired, the function returns an empty string
    """
    phone_text = phone.encode('ascii', 'ignore')  # encode to ascii
    phone_text = phone_text.lower()
    phone_text = phone_text.strip()
    extension_digits = None
    #
    # strip off US international country code
    #
    if phone_text.find('+1 ') == 0:
        phone_text = phone_text[3:]
    if phone_text.find('+1-') == 0:
        phone_text = phone_text[3:]
    if phone_text.find('(1)') == 0:
        phone_text = phone_text[3:]
    digits = []
    for c in list(phone_text):
        if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            digits.append(c)
    if len(digits) > 10 or phone_text.rfind('x') > -1:
        # pull off the extension
        i = phone_text.rfind(' ')  # last blank
        if i > 0:
            extension = phone_text[i + 1:]
            extension_digits = []
            for c in list(extension):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    extension_digits.append(c)
            digits = []  # reset the digits
            for c in list(phone_text[:i + 1]):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    digits.append(c)
        elif phone_text.rfind('x') > 0:
            i = phone_text.rfind('x')
            extension = phone_text[i + 1:]
            extension_digits = []
            for c in list(extension):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    extension_digits.append(c)
            digits = []  # recalculate the digits
            for c in list(phone_text[:i + 1]):
                if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    digits.append(c)
        else:
            extension_digits = digits[10:]
            digits = digits[:10]
    if len(digits) == 7:
        if phone[0:5] == '352392':
            updated_phone = ''  # Damaged UF phone number, nothing to repair
            extension_digits = None
        elif phone[0:5] == '352273':
            updated_phone = ''  # Another damaged phone number, not to repair
            extension_digits = None
        else:
            updated_phone = '(352) ' + "".join(digits[0:3]) + '-' + "".join(digits[3:7])
    elif len(digits) == 10:
        updated_phone = '(' + "".join(digits[0:3]) + ') ' + "".join(digits[3:6]) + \
                        '-' + "".join(digits[6:10])
    elif len(digits) == 5 and digits[0] == '2':  # UF special
        updated_phone = '(352) 392-' + "".join(digits[1:5])
    elif len(digits) == 5 and digits[0] == '3':  # another UF special
        updated_phone = '(352) 273-' + "".join(digits[1:5])
    else:
        updated_phone = ''  # no repair
        extension_digits = None
    if extension_digits is not None and len(extension_digits) > 0:
        updated_phone = updated_phone + ' ext. ' + "".join(extension_digits)
    if debug:
        print phone.ljust(25), updated_phone.ljust(25)
    return updated_phone


def comma_space(s):
    """
    insert a space after every comma in s unless s ends in a comma
    :param s: string to be checked for spaces after commas
    :return s: improved string with commas always followed by spaces
    :rtype: basestring
    """
    k = s.find(',')
    if -1 < k < len(s) - 1 and s[k + 1] != " ":
        s = s[0:k] + ', ' + comma_space(s[k + 1:])
    return s


def improve_course_title(s):
    """
    The Office of the University Registrar at UF uses a series of abbreviations to fit course titles into limited text
    strings.
    Here we attempt to reverse the process -- a short title is turned into a
    longer one for use in labels
    """

    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '       # add a trailing space so we can find these abbreviated
                   # words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace("-", " #")

    t = t.replace(" @", "/")  # restore /
    t = t.replace(" @", "/")  # restore /
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" #", "-")  # restore -
    t = comma_space(t.strip())
    return t[0].upper() + t[1:]


def improve_jobcode_description(s):
    """
    HR uses a series of abbreviations to fit job titles into limited text
    strings.
    Here we attempt to reverse the process -- a short title is turned into a
    longer one for use in position labels
    """

    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '       # add a trailing space so we can find these abbreviated
                   # words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace("&", " and ")
    t = t.replace("Aca ", "Academic ")
    t = t.replace("Act ", "Acting ")
    t = t.replace("Advanc ", "Advanced ")
    t = t.replace("Adv ", "Advisory ")
    t = t.replace("Agric ", "Agricultural ")
    t = t.replace("Alumn Aff ", "Alumni Affairs ")
    t = t.replace("Anal  ", "Analyst ")
    t = t.replace("Asst ", "Assistant ")
    t = t.replace("Ast #R ", "Research Assistant ")
    t = t.replace("Ast #G ", "Grading Assistant ")
    t = t.replace("Ast #T ", "Teaching Assistant ")
    t = t.replace("Ast ", "Assistant ")
    t = t.replace("Asst. ", "Assistant ")
    t = t.replace("Affl ", "Affiliate ")
    t = t.replace("Aso ", "Associate ")
    t = t.replace("Asoc ", "Associate ")
    t = t.replace("Assoc ", "Associate ")
    t = t.replace("Bio ", "Biological ")
    t = t.replace("Prof ", "Professor ")
    t = t.replace("Mstr ", "Master ")
    t = t.replace("Couns ", "Counselor ")
    t = t.replace("Adj ", "Adjunct ")
    t = t.replace("Dist ", "Distinguished ")
    t = t.replace("Chem", "Chemist")
    t = t.replace("Chr ", "Chair ")
    t = t.replace("Cio ", "Chief Information Officer ")
    t = t.replace("Comm", "Communications")
    t = t.replace("Coo ", "Chief Operating Officer ")
    t = t.replace("Coord ", "Coordinator ")
    t = t.replace("Co ", "Courtesy ")
    t = t.replace("Clin ", "Clinical ")
    t = t.replace("Clrk", "Clerk")
    t = t.replace("Ctsy", "Courtesy")
    t = t.replace("Dn ", "Dean ")
    t = t.replace("Div ", "Division ")
    t = t.replace("Fin", "Financial")
    t = t.replace("Finan ", "Financial ")
    t = t.replace("Stu ", "Student ")
    t = t.replace("Prg ", "Program ")
    t = t.replace("Dev ", "Development ")
    t = t.replace("Aff ", "Affiliate ")
    t = t.replace("Svcs ", "Services ")
    t = t.replace("Devel ", "Development ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Progs ", "Programs ")
    t = t.replace("Facil ", "Facility ")
    t = t.replace("Hlt", "Health")
    t = t.replace("Hlth ", "Health ")
    t = t.replace("Int ", "Interim ")
    t = t.replace("Sctst ", "Scientist ")
    t = t.replace("Supp ", "Support ")
    t = t.replace("Cty ", "County ")
    t = t.replace("Ext ", "Extension ")
    t = t.replace("Emer ", "Emeritus ")
    t = t.replace("Enforce ", "Enforcement ")
    t = t.replace("Environ ", "Environmental ")
    t = t.replace("Gen ", "General ")
    t = t.replace("Grd", "Graduate")
    t = t.replace("Jnt ", "Joint ")
    t = t.replace("Jr", "Junior")
    t = t.replace("Eng ", "Engineer ")
    t = t.replace("Ctr ", "Center ")
    t = t.replace("Opr ", "Operator ")
    t = t.replace("Admin ", "Administrative ")
    t = t.replace("Dis ", "Distinguished ")
    t = t.replace("Ser ", "Service ")
    t = t.replace("Rep ", "Representative ")
    t = t.replace("Radiol ", "Radiology ")
    t = t.replace("Technol ", "Technologist ")
    t = t.replace("Pres ", "President ")
    t = t.replace("Pres5 ", "President 5 ")
    t = t.replace("Pres6 ", "President 6 ")
    t = t.replace("Emin ", "Eminent ")
    t = t.replace("Cfo ", "Chief Financial Officer ")
    t = t.replace("Prov ", "Provisional ")
    t = t.replace("Adm ", "Administrator ")
    t = t.replace("Info ", "Information ")
    t = t.replace("It ", "Information Technology ")
    t = t.replace("Mgr ", "Manager ")
    t = t.replace("Mgt ", "Management ")
    t = t.replace("Vis ", "Visiting ")
    t = t.replace("Lect ", "Lecturer ")
    t = t.replace("Phas ", "Phased ")
    t = t.replace("Prog ", "Programmer ")
    t = t.replace("Prof. ", "Professor ")
    t = t.replace("Pract ", "Practitioner ")
    t = t.replace("Registr ", "Registration ")
    t = t.replace("Rsch ", "Research ")
    t = t.replace("Rsrh ", "Research ")
    t = t.replace("Ret ", "Retirement ")
    t = t.replace("Sch ", "School ")
    t = t.replace("Sci ", "Scientist ")
    t = t.replace("Svcs ", "Services ")
    t = t.replace("Serv ", "Service ")
    t = t.replace("Tch ", "Teaching ")
    t = t.replace("Tele ", "Telecommunications ")
    t = t.replace("Tv ", "TV ")
    t = t.replace("Univ ", "University ")
    t = t.replace("Educ ", "Education ")
    t = t.replace("Crd ", "Coordinator ")
    t = t.replace("Res ", "Research ")
    t = t.replace("Dir ", "Director ")
    t = t.replace("Pky ", "PK Yonge ")
    t = t.replace("Rcv ", "Receiving ")
    t = t.replace("Sr ", "Senior ")
    t = t.replace("Spec ", "Specialist ")
    t = t.replace("Spc ", "Specialist ")
    t = t.replace("Spv ", "Supervisor ")
    t = t.replace("Supv ", "Supervisor ")
    t = t.replace("Supt ", "Superintendant ")
    t = t.replace("Stud", "Student")
    t = t.replace("Pky ", "P. K. Yonge ")
    t = t.replace("Ii ", "II ")
    t = t.replace("Iii ", "III ")
    t = t.replace("Iv ", "IV ")
    t = t.replace("Communic ", "Communications ")
    t = t.replace("Postdoc ", "Postdoctoral ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Vp ", "Vice President ")
    t = t.replace(" @", "/")  # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" #", "-")  # restore -
    return t[:-1]  # Take off the trailing space


def improve_title(s):
    """
    DSP, HR, funding agencies and others use a series of abbreviations to fit grant titles into limited text
    strings.  Systems often restrict the length of titles of various kinds and
    faculty often clip their titles to fit in available space.  Here we reverse
    the process and lengthen the name for readability
    :param s:
    :return:
    :rtype: basestring
    """
    if s == "":
        return s
    if s[len(s) - 1] == ',':
        s = s[0:len(s) - 1]
    if s[len(s) - 1] == ',':
        s = s[0:len(s) - 1]
    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '    # add a trailing space so we can find these abbreviated words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace(",", " !")  # might be two commas in input
    t = t.replace("'S ", "'s ")
    t = t.replace("2-blnd ", "Double-blind ")
    t = t.replace("2blnd ", "Double-blind ")
    t = t.replace("A ", "a ")
    t = t.replace("Aav ", "AAV ")
    t = t.replace("Aca ", "Academic ")
    t = t.replace("Acad ", "Academic ")
    t = t.replace("Acp ", "ACP ")
    t = t.replace("Acs ", "ACS ")
    t = t.replace("Act ", "Acting ")
    t = t.replace("Adj ", "Adjunct ")
    t = t.replace("Adm ", "Administrator ")
    t = t.replace("Admin ", "Administrative ")
    t = t.replace("Adv ", "Advisory ")
    t = t.replace("Advanc ", "Advanced ")
    t = t.replace("Aff ", "Affiliate ")
    t = t.replace("Affl ", "Affiliate ")
    t = t.replace("Ahec ", "AHEC ")
    t = t.replace("Aldh ", "ALDH ")
    t = t.replace("Alk1 ", "ALK1 ")
    t = t.replace("Alumn Aff ", "Alumni Affairs ")
    t = t.replace("Amd3100 ", "AMD3100 ")
    t = t.replace("And ", "and ")
    t = t.replace("Aso ", "Associate ")
    t = t.replace("Asoc ", "Associate ")
    t = t.replace("Assoc ", "Associate ")
    t = t.replace("Ast ", "Assistant ")
    t = t.replace("Ast #G ", "Grading Assistant ")
    t = t.replace("Ast #R ", "Research Assistant ")
    t = t.replace("Ast #T ", "Teaching Assistant ")
    t = t.replace("At ", "at ")
    t = t.replace("Bldg ", "Building ")
    t = t.replace("Bpm ", "BPM ")
    t = t.replace("Brcc ", "BRCC ")
    t = t.replace("Cfo ", "Chief Financial Officer ")
    t = t.replace("Cio ", "Chief Information Officer ")
    t = t.replace("Clin ", "Clinical ")
    t = t.replace("Clncl ", "Clinical ")
    t = t.replace("Cms ", "CMS ")
    t = t.replace("Cns ", "CNS ")
    t = t.replace("Cncr ", "Cancer ")
    t = t.replace("Co ", "Courtesy ")
    t = t.replace("Cog ", "COG ")
    t = t.replace("Communic ", "Communications ")
    t = t.replace("Compar ", "Compare ")
    t = t.replace("Coo ", "Chief Operating Officer ")
    t = t.replace("Copd ", "COPD ")
    t = t.replace("Cpb ", "CPB ")
    t = t.replace("Crd ", "Coordinator ")
    t = t.replace("Cse ", "CSE ")
    t = t.replace("Ctr ", "Center ")
    t = t.replace("Cty ", "County ")
    t = t.replace("Cwp ", "CWP ")
    t = t.replace("Dbl-bl ", "Double-blind ")
    t = t.replace("Dbl-blnd ", "Double-blind ")
    t = t.replace("Dbs ", "DBS ")
    t = t.replace("Dev ", "Development ")
    t = t.replace("Devel ", "Development ")
    t = t.replace("Dist ", "Distinguished ")
    t = t.replace("Dna ", "DNA ")
    t = t.replace("Doh ", "DOH ")
    t = t.replace("Doh/cms ", "DOH/CMS ")
    t = t.replace("Double Blinded ", "Double-blind ")
    t = t.replace("Double-blinded ", "Double-blind ")
    t = t.replace("Dpt-1 ", "DPT-1 ")
    t = t.replace("Dtra0001 ", "DTRA0001 ")
    t = t.replace("Dtra0016 ", "DTRA-0016 ")
    t = t.replace("Educ ", "Education ")
    t = t.replace("Eff/saf ", "Safety and Efficacy ")
    t = t.replace("Eh&S ", "EH&S ")
    t = t.replace("Emer ", "Emeritus ")
    t = t.replace("Emin ", "Eminent ")
    t = t.replace("Enforce ", "Enforcement ")
    t = t.replace("Eng ", "Engineer ")
    t = t.replace("Environ ", "Environmental ")
    t = t.replace("Epr ", "EPR ")
    t = t.replace("Eval ", "Evaluation ")
    t = t.replace("Ext ", "Extension ")
    t = t.replace("Fdot ", "FDOT ")
    t = t.replace("Fdots ", "FDOT ")
    t = t.replace("Fhtcc ", "FHTCC ")
    t = t.replace("Finan ", "Financial ")
    t = t.replace("Fla ", "Florida ")
    t = t.replace("Fllw ", "Follow ")
    t = t.replace("For ", "for ")
    t = t.replace("G-csf ", "G-CSF ")
    t = t.replace("Gen ", "General ")
    t = t.replace("Gis ", "GIS ")
    t = t.replace("Gm-csf ", "GM-CSF ")
    t = t.replace("Grad ", "Graduate ")
    t = t.replace("Hcv ", "HCV ")
    t = t.replace("Hiv ", "HIV ")
    t = t.replace("Hiv-infected ", "HIV-infected ")
    t = t.replace("Hiv/aids ", "HIV/AIDS ")
    t = t.replace("Hlb ", "HLB ")
    t = t.replace("Hlth ", "Health ")
    t = t.replace("Hou ", "Housing ")
    t = t.replace("Hsv-1 ", "HSV-1 ")
    t = t.replace("I/ii ", "I/II ")
    t = t.replace("I/ucrc ", "I/UCRC ")
    t = t.replace("Ica ", "ICA ")
    t = t.replace("Icd ", "ICD ")
    t = t.replace("Ieee ", "IEEE ")
    t = t.replace("Ifas ", "IFAS ")
    t = t.replace("Igf-1 ", "IGF-1 ")
    t = t.replace("Ii ", "II ")
    t = t.replace("Ii/iii ", "II/III ")
    t = t.replace("Iii ", "III ")
    t = t.replace("In ", "in ")
    t = t.replace("Info ", "Information ")
    t = t.replace("Inter-vention ", "Intervention ")
    t = t.replace("Ipa ", "IPA ")
    t = t.replace("Ipm ", "IPM ")
    t = t.replace("Ippd ", "IPPD ")
    t = t.replace("Ips ", "IPS ")
    t = t.replace("It ", "Information Technology ")
    t = t.replace("Iv ", "IV ")
    t = t.replace("Jnt ", "Joint ")
    t = t.replace("Lng ", "Long ")
    t = t.replace("Mccarty ", "McCarty ")
    t = t.replace("Mgmt ", "Management ")
    t = t.replace("Mgr ", "Manager ")
    t = t.replace("Mgt ", "Management ")
    t = t.replace("Mlti ", "Multi ")
    t = t.replace("Mlti-ctr ", "Multicenter ")
    t = t.replace("Mltictr ", "Multicenter ")
    t = t.replace("Mri ", "MRI ")
    t = t.replace("Mstr ", "Master ")
    t = t.replace("Multi-center ", "Multicenter ")
    t = t.replace("Multi-ctr ", "Multicenter ")
    t = t.replace("Nih ", "NIH ")
    t = t.replace("Nmr ", "NMR ")
    t = t.replace("Nsf ", "NSF ")
    t = t.replace("Ne ", "NE ")
    t = t.replace("Nw ", "NW ")
    t = t.replace("Of ", "of ")
    t = t.replace("On ", "on ")
    t = t.replace("Or ", "or ")
    t = t.replace("Open-labeled ", "Open-label ")
    t = t.replace("Opn-lbl ", "Open-label ")
    t = t.replace("Opr ", "Operator ")
    t = t.replace("Phas ", "Phased ")
    t = t.replace("Php ", "PHP ")
    t = t.replace("Phs ", "PHS ")
    t = t.replace("Pk/pd ", "PK/PD ")
    t = t.replace("Pky ", "P. K. Yonge ")
    t = t.replace("Pky ", "PK Yonge ")
    t = t.replace("Plcb-ctrl ", "Placebo-controlled ")
    t = t.replace("Plcbo ", "Placebo ")
    t = t.replace("Plcbo-ctrl ", "Placebo-controlled ")
    t = t.replace("Postdoc ", "Postdoctoral ")
    t = t.replace("Pract ", "Practitioner ")
    t = t.replace("Pres5 ", "President 5 ")
    t = t.replace("Pres6 ", "President 6 ")
    t = t.replace("Prg ", "Programs ")
    t = t.replace("Prof ", "Professor ")
    t = t.replace("Prog ", "Programmer ")
    t = t.replace("Progs ", "Programs ")
    t = t.replace("Prov ", "Provisional ")
    t = t.replace("Psr ", "PSR ")
    t = t.replace("Radiol ", "Radiology ")
    t = t.replace("Rcv ", "Receiving ")
    t = t.replace("Rdmzd ", "Randomized ")
    t = t.replace("Rep ", "Representative ")
    t = t.replace("Res ", "Research ")
    t = t.replace("Ret ", "Retirement ")
    t = t.replace("Reu ", "REU ")
    t = t.replace("Rna ", "RNA ")
    t = t.replace("Rndmzd ", "Randomized ")
    t = t.replace("Roc-124 ", "ROC-124 ")
    t = t.replace("Rsch ", "Research ")
    t = t.replace("Saf ", "SAF ")
    t = t.replace("Saf/eff ", "Safety and Efficacy ")
    t = t.replace("Sbjcts ", "Subjects ")
    t = t.replace("Sch ", "School ")
    t = t.replace("Se ", "SE ")
    t = t.replace("Ser ", "Service ")
    t = t.replace("Sfwmd ", "SFWMD ")
    t = t.replace("Sle ", "SLE ")
    t = t.replace("Sntc ", "SNTC ")
    t = t.replace("Spec ", "Specialist ")
    t = t.replace("Spnsrd ", "Sponsored ")
    t = t.replace("Spv ", "Supervisor ")
    t = t.replace("Sr ", "Senior ")
    t = t.replace("Stdy ", "Study ")
    t = t.replace("Subj ", "Subject ")
    t = t.replace("Supp ", "Support ")
    t = t.replace("Supt ", "Superintendant ")
    t = t.replace("Supv ", "Supervisor ")
    t = t.replace("Svc ", "Services ")
    t = t.replace("Svcs ", "Services ")
    t = t.replace("Sw ", "SW ")
    t = t.replace("Tch ", "Teaching ")
    t = t.replace("Tech ", "Technician ")
    t = t.replace("Technol ", "Technologist ")
    t = t.replace("Teh ", "the ")
    t = t.replace("The ", "the ")
    t = t.replace("To ", "to ")
    t = t.replace("Trls ", "Trials ")
    t = t.replace("Trm ", "Term ")
    t = t.replace("Tv ", "TV ")
    t = t.replace("Uaa ", "UAA ")
    t = t.replace("Uf ", "UF ")
    t = t.replace("Ufrf ", "UFRF ")
    t = t.replace("Uhf ", "UHF ")
    t = t.replace("Univ ", "University ")
    t = t.replace("Us ", "US ")
    t = t.replace("Usa ", "USA ")
    t = t.replace("Va ", "VA ")
    t = t.replace("Vhf ", "VHF ")
    t = t.replace("Vis ", "Visiting ")
    t = t.replace("Vp ", "Vice President ")
    t = t.replace("Wuft-Fm ", "WUFT-FM ")
    t = t.replace(" @", "/")  # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" !", ",")  # restore ,
    t = comma_space(t.strip())
    return t[0].upper() + t[1:]


def improve_dollar_amount(s):
    """
    given a text string s that should be a dollar amount, return a string that looks like n*.nn
    :param s: the string to be improved
    :return: the improved string
    """
    import re
    pattern = re.compile('[0-9]*[0-9]\.[0-9][0-9]')
    s = s.replace(' ', '')
    s = s.replace('$', '')
    s = s.replace(',', '')
    if '.' not in s:
        s += '.00'
    if s[0] == '.':
        s = '0' + s
    m = pattern.match(s)
    if not m:
        raise InvalidDataException(s + ' not a valid dollar amount')
    return s


def improve_date(s):
    """
    Given a string representing a date, year month day, return a string that is standard UTC format.
    :param s: the string to be improved.  Several input date formats are supported including slashes, spaces or dashes
    for separators, variable digits for year, month and day.
    :return: improved date string
    :rtype: string
    """
    import re
    from datetime import date

    month_words = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11,
        'dec': 12, 'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    all_numbers = re.compile('([0-9]+)[-/, ]([0-9]+)[-/, ]([0-9]+)')
    middle_word = re.compile('([0-9]+)[-/, ]([a-zA-Z]+)[-,/ ]([0-9]+)')
    match_object = all_numbers.match(s)
    if match_object:
        y = int(match_object.group(1))
        m = int(match_object.group(2))
        d = int(match_object.group(3))
    else:
        match_object = middle_word.match(s)
        if match_object:
            y = int(match_object.group(1))
            m = month_words.get(match_object.group(2).lower(), None)
            if m is None:
                raise InvalidDataException(s + ' is not a valid date')
            d = int(match_object.group(3))
        else:
            raise InvalidDataException(s + ' did not match a date pattern')
    if y < 100:
        y += 2000
    date_value = date(y, m, d)
    date_string = date_value.isoformat()
    return date_string


def improve_deptid(s):
    """
    Given a string with a deptid, confirm validity, add leading zeros if needed
    :param s: string deptid
    :return: string improved deptid
    :rtype: string
    """
    import re
    deptid_pattern = re.compile('([0-9]{1,8})')
    match_object = deptid_pattern.match(s)
    if match_object:
        return match_object.group(1).rjust(8, '0')
    else:
        raise InvalidDataException(s + ' is not a valid deptid')


def improve_display_name(s):
    """
    Give a display name s, fix it up into a standard format -- last name, comma, first name (or initial), middle name
    or initials.  Initials are followed with a period and a space.  No trailing space at the end of the display_name
    :param s: Display names in a variety of formats
    :return: standard display name
    """
    s = s.title()  # Capitalize each word
    s = comma_space(s)  # put a blank after the comma
    s = s.strip()  # remove trailing spaces
    return s


def improve_sponsor_award_id(s):
    """
    Given a string with a sponsor award id, standardize presentation and regularize NIH award ids
    :param s: string with sponsor award id
    :return: string improved sponsor award id
    :rtype: string
    """
    import re
    s = s.strip()
    nih_pattern = re.compile('.*([A-Za-z][0-9][0-9]).*([A-Za-z][A-Za-z][0-9]{6})')
    match_object = nih_pattern.match(s)
    if match_object:
        return match_object.group(1).upper() + match_object.group(2).upper()
    else:
        return s


def parse_pages(pages):
    """
    Give a string possibly containing a start and end page, return the start and end page if any
    :param pages:
    :return: list with start and end pages
    """
    if '-' in pages:
        k = pages.find('-')
        start = pages[0:k]
        end = pages[k + 1:]
    else:
        start = pages
        end = ''
    return [start, end]


def parse_date_parts(month, year):
    """
    Given a mont string and a year string from publisher data, parse apart the month, day and year and create
    a standard date string that can be used as input to VIVO
    :param month: string from publisher data.  May be text such as 'JUN' or 'Jun 15' with day number included
    :param year: string of year such as '2015'
    :return: date string in isoformat
    """
    month_numbers = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                     'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
                     'SUM': 6, 'FAL': 9, 'WIN': 12, 'SPR': 3, '': 1}
    from datetime import datetime
    if ' ' in month:
        k = month.find(' ')
        month_name = month[0:k]
        month_day = month[k + 1:]
    elif '-' in month:
        k = month.find('-')
        month_name = month[0:k]
        month_day = '1'
    else:
        month_name = month
        month_day = '1'
    month_number = month_numbers[month_name.upper()]
    date_value = datetime(int(year), month_number, int(month_day))
    return date_value.isoformat()
