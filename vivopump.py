#!/usr/bin/env/python
""" vivopump -- module of helper functions for the pump
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2015 Michael Conlon"
__license__ = "New BSD license"
__version__ = "0.6.6"

import csv
import string
import random


class InvalidDefException(Exception):
    """
    Raise this exception when update definition contains values that can not be processed
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidDataException(Exception):
    """
    Raise this exception when update data contains values that can not be processed
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class PathLengthException(Exception):
    """
    Raise this exception when update def has a path length greater than support
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
    var_names = data[data.keys()[0]].keys()  # create a list of var_names from the first row
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


def get_vivo_types(selector, parms, separator=';'):
    """
    Query VIVO using the selector and return a dictionary with keys of all uri satisfying the selector and
    data of all the types for each uri, separated by the separator
    :param: selector: query fragment for selecting the entities whose types will be returned
    :param: parms: vivo_query parms
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
    a = vivo_query(q, parms)
    types = [x['types']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(uri, types))


def get_vivo_ufid(parms):
    """
    Query VIVO and return a list of all the ufid found in VIVO
    :param: parms: vivo_query parameters
    :return: dictionary of uri keyed by ufid
    """
    query = "select ?uri ?ufid where {?uri uf:ufid ?ufid .}"
    a = vivo_query(query, parms)
    ufid = [x['ufid']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(ufid, uri))


def get_vivo_publishers(parms):
    """
    Query VIVO and return a list of all the publishers found in VIVO
    :param: parms: vivo_query parameters
    :return: dictionary of uri keyed by simplified publisher name
    """
    query = "select ?uri ?label where {?uri a vivo:Publisher . ?uri rdfs:label ?label .}"
    a = vivo_query(query, parms)
    label = [key_string(x['label']['value']) for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(label, uri))


def get_vivo_journals(parms):
    """
    Query VIVO and return a list of all the journals found in VIVO
    :param: parms: vivo_query params
    :return: dictionary of uri keyed by ISSN
    """
    query = "select ?uri ?issn where {?uri bibo:issn ?issn .}"
    a = vivo_query(query, parms)
    issn = [x['issn']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(issn, uri))


def get_vivo_ccn(parms):
    """
    Query VIVO and return a list of all the ccn found in VIVO
    :param: parms: vivo_query parms
    :return: dictionary of uri keyed by ccn
    """
    query = "select ?uri ?ccn where {?uri uf:ccn ?ccn .}"
    a = vivo_query(query, parms)
    ccn = [x['ccn']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(ccn, uri))


def get_vivo_sponsorid(parms):
    """
    Query VIVO and return a list of all the sponsorid found in VIVO
    :param: parms: vivo_query parms
    :return: dictionary of uri keyed by sponsorid
    """
    query = "select ?uri ?sponsorid where {?uri uf:sponsorId ?sponsorid .}"
    a = vivo_query(query, parms, parms['verbose'])
    sponsorid = [x['sponsorid']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(sponsorid, uri))


def get_vivo_authors(parms):
    """
    Query VIVO and return a list of all the authors found in VIVO.  Authors are people connected to
    publications through authorships
    :param: parms: vivo_query parms
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
    a = vivo_query(query, parms)
    display_name = [x['display_name']['value'] for x in a['results']['bindings']]
    uri = [x['uri']['value'] for x in a['results']['bindings']]
    return dict(zip(display_name, uri))


def get_vivo_positions(parms):
    """
    Query VIVO and return a list of all the UF positions found in VIVO.  UF positions will
    have an hrTitle.  Non UF positions will not have this property
    :param: parms: vivo_query parameters
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
    a = vivo_query(query, parms)
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
        Given an update_def (a) and the string of the input file containing the update_def (b),
        add an "order" parameter to the entity_def, specifying the column_def ordering.  This
        is used in subsequent processing to insure that the order in the input file is preserved
        when output is created.
        :param a: update_def
        :param b: string of update_def from file
        :return a new update_def dictionary with an order list in the entity def
        """
        defn = a
        loc = []
        var_list = []
        k = b.find("column_defs")
        b = b[k:]
        for var in defn['column_defs'].keys():
            var_list.append(var)
            loc.append(b.find(var + '": ['))
        seq = sorted(loc)
        order = [var_list[loc.index(v)] for v in seq]
        defn['entity_def']['order'] = order
        return defn

    def validate_update_def(a):
        """
        Validate the update_def.  Throw InvalidDef if errors
        :param a: update_def
        :return None
        """
        names = [y[x]['object'].get('name', '') for y in a['column_defs'].values() for x in range(len(y))]
        col_names = a['column_defs'].keys()
        for name in col_names:
            if name in names:
                raise InvalidDefException(name + " in object and column_defs")
        return None

    import json
    with open(filename, "r") as my_file:
        data = my_file.read()
        update_def = fixit(json.loads(data))
        update_def = add_order(update_def, data)
        validate_update_def(update_def)
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


def get_graph(update_def, query_parms, debug=False):
    """
    Given the update def, get a graph from VIVO of the triples eligible for updating
    :return: graph of triples
    """

    from rdflib import Graph, URIRef

    a = Graph()
    entity_query = 'select ?uri (<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> as ?p) (<' + \
        str(update_def['entity_def']['type']) + '> as ?o)\nwhere {\n    ' + \
        update_def['entity_def']['entity_sparql'] + '\n}'
    result = vivo_query(entity_query, query_parms, debug=debug)
    for row in result['results']['bindings']:
        s = URIRef(row['uri']['value'])
        p = URIRef(row['p']['value'])
        o = make_rdf_term(row['o'])
        a.add((s, p, o))
    for path in update_def['column_defs'].values():
        update_query = make_update_query(update_def['entity_def']['entity_sparql'], path)
        if len(update_query) == 0:
            continue
        result = vivo_query(update_query, query_parms, debug=debug)
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


def new_uri(parms):
    """
    Find an unused VIVO URI in the VIVO defined by the parms
    :param parms: dictionary with queryuri, username, password and uriprefix
    :return: a URI not in VIVO
    """
    test_uri = ""
    while True:
        test_uri = parms['uriprefix'] + str(random.randint(1, 9999999999))
        query = """
            SELECT (COUNT(?z) AS ?count) WHERE {
            <""" + test_uri + """> ?y ?z
            }"""
        response = vivo_query(query, parms)
        if int(response["results"]["bindings"][0]['count']['value']) == 0:
            break
    return test_uri


def vivo_query(query, parms, debug=False):
    """
    A new VIVO query function using SPARQLWrapper.  Tested with Stardog, UF VIVO and Dbpedia
    :param query: SPARQL query.  VIVO PREFIX will be added
    :param parms: dictionary with query parms:  queryuri, username and password
    :param debug: boolean. If true, query will be printed to stdout
    :return: result object, typically JSON
    :rtype: dict
    """
    from SPARQLWrapper import SPARQLWrapper, JSON
    import sys

    if debug:
        print >>sys.stderr, "in vivo_query"
        print >>sys.stderr, parms
    sparql = SPARQLWrapper(parms['queryuri'])
    new_query = parms['prefix'] + '\n' + query
    sparql.setQuery(new_query)
    if debug:
        print >>sys.stderr, new_query
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
    abbrev_table = {
        "Intro ": "Introduction ",
        "To ": "to ",
        "Of ": "of ",
        "In ": "in ",
        "Stat ": "Statistics ",
        "Spec ": "Special ",
        "Top ": "Topics ",
        "Hist ": "History ",
        "Hlthcare ": "Healthcare ",
        "Prac ": "Practice "
    }
    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '       # add a trailing space so we can find these abbreviated words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace("-", " #")
    for abbrev in abbrev_table:
        t = t.replace(abbrev, abbrev_table[abbrev])
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
    abbrev_table = {
        "Aca ": "Academic ",
        "Act ": "Acting ",
        "Adj ": "Adjunct ",
        "Adm ": "Administrator ",
        "Admin ": "Administrative ",
        "Adv ": "Advisory ",
        "Advanc ": "Advanced ",
        "Aff ": "Affiliate ",
        "Affl ": "Affiliate ",
        "Agric ": "Agricultural ",
        "Alumn Aff ": "Alumni Affairs ",
        "Anal  ": "Analyst ",
        "Anlst ": "Analyst ",
        "Aso ": "Associate ",
        "Asoc ": "Associate ",
        "Assoc ": "Associate ",
        "Asst ": "Assistant ",
        "Asst. ": "Assistant ",
        "Ast ": "Assistant ",
        "Ast #G ": "Grading Assistant ",
        "Ast #R ": "Research Assistant ",
        "Ast #T ": "Teaching Assistant ",
        "Bio ": "Biological ",
        "Cfo ": "Chief Financial Officer ",
        "Chem ": "Chemist ",
        "Chr ": "Chair ",
        "Cio ": "Chief Information Officer ",
        "Clin ": "Clinical ",
        "Clrk ": "Clerk ",
        "Co ": "Courtesy ",
        "Comm ": "Communications ",
        "Communic ": "Communications ",
        "Coo ": "Chief Operating Officer ",
        "Coord ": "Coordinator ",
        "Couns ": "Counselor ",
        "Crd ": "Coordinator ",
        "Ctr ": "Center ",
        "Ctsy ": "Courtesy ",
        "Cty ": "County ",
        "Dev ": "Development ",
        "Devel ": "Development ",
        "Dir ": "Director ",
        "Dis ": "Distinguished ",
        "Dist ": "Distinguished ",
        "Div ": "Division ",
        "Dn ": "Dean ",
        "Educ ": "Education ",
        "Emer ": "Emeritus ",
        "Emin ": "Eminent ",
        "Enforce ": "Enforcement ",
        "Eng ": "Engineer ",
        "Environ ": "Environmental ",
        "Ext ": "Extension ",
        "Facil ": "Facility ",
        "Fin ": "Financial",
        "Finan ": "Financial ",
        "Gen ": "General ",
        "Grd ": "Graduate ",
        "Hlt ": "Health ",
        "Hlth ": "Health ",
        "Ii ": "II ",
        "Iii ": "III ",
        "Info ": "Information ",
        "Int ": "Interim ",
        "It ": "Information Technology ",
        "Iv ": "IV ",
        "Jnt ": "Joint ",
        "Jr": "Junior",
        "Lect ": "Lecturer ",
        "Mgr ": "Manager ",
        "Mgt ": "Management ",
        "Mstr ": "Master ",
        "Opr ": "Operator ",
        "Phas ": "Phased ",
        "Pky ": "PK Yonge ",
        "Postdoc ": "Postdoctoral ",
        "Pract ": "Practitioner ",
        "Pres ": "President ",
        "Pres5 ": "President 5 ",
        "Pres6 ": "President 6 ",
        "Prg ": "Program ",
        "Prof ": "Professor ",
        "Prof. ": "Professor ",
        "Prog ": "Programmer ",
        "Progs ": "Programs ",
        "Prov ": "Provisional ",
        "Radiol ": "Radiology ",
        "Rcv ": "Receiving ",
        "Registr ": "Registration ",
        "Rep ": "Representative ",
        "Res ": "Research ",
        "Ret ": "Retirement ",
        "Rsch ": "Research ",
        "Rsrh ": "Research ",
        "Sch ": "School ",
        "Sci ": "Scientist ",
        "Sctst ": "Scientist ",
        "Ser ": "Service ",
        "Serv ": "Service ",
        "Spc ": "Specialist ",
        "Spec ": "Specialist ",
        "Spv ": "Supervisor ",
        "Sr ": "Senior ",
        "Stu ": "Student ",
        "Stud ": "Student",
        "Supp ": "Support ",
        "Supt ": "Superintendent ",
        "Supv ": "Supervisor ",
        "Svcs ": "Services ",
        "Tch ": "Teaching ",
        "Tech ": "Technician ",
        "Technol ": "Technologist ",
        "Tele ": "Telecommunications ",
        "Tv ": "TV ",
        "Univ ": "University ",
        "Vis ": "Visiting ",
        "Vp ": "Vice President "
    }
    s = s.lower()  # convert to lower
    s = s.title()  # uppercase each word
    s += ' '       # add a trailing space so we can find these abbreviated words throughout the string
    t = s.replace(", ,", ",")
    t = t.replace("  ", " ")
    t = t.replace("/", " @")
    t = t.replace("/", " @")  # might be two slashes in the input
    t = t.replace(",", " !")
    t = t.replace("&", " and ")
    for abbrev in abbrev_table:
        t = t.replace(abbrev, abbrev_table[abbrev])
    t = t.replace(" @", "/")  # restore /
    t = t.replace(" @", "/")
    t = t.replace(" !", ",")  # restore ,
    t = t.replace(" #", "-")  # restore -
    return t[:-1]  # Take off the trailing space


def improve_title(s):
    """
    DSP, HR, funding agencies and others use a series of abbreviations to fit grant titles into limited text
    strings.  Systems often restrict the length of titles of various kinds and faculty often clip their titles to
    fit in available space.  Here we reverse the process and lengthen the name for readability
    :param s:
    :return:
    :rtype: basestring
    """
    abbrev_table = {
        "'S ": "'s ",
        "2-blnd ": "Double-blind ",
        "2blnd ": "Double-blind ",
        "A ": "a ",
        "Aav ": "AAV ",
        "Aca ": "Academic ",
        "Acad ": "Academic ",
        "Acp ": "ACP ",
        "Acs ": "ACS ",
        "Act ": "Acting ",
        "Adj ": "Adjunct ",
        "Adm ": "Administrator ",
        "Admin ": "Administrative ",
        "Adv ": "Advisory ",
        "Advanc ": "Advanced ",
        "Aff ": "Affiliate ",
        "Affl ": "Affiliate ",
        "Ahec ": "AHEC ",
        "Aldh ": "ALDH ",
        "Alk1 ": "ALK1 ",
        "Alumn Aff ": "Alumni Affairs ",
        "Amd3100 ": "AMD3100 ",
        "And ": "and ",
        "Aso ": "Associate ",
        "Asoc ": "Associate ",
        "Assoc ": "Associate ",
        "Ast ": "Assistant ",
        "Ast #G ": "Grading Assistant ",
        "Ast #R ": "Research Assistant ",
        "Ast #T ": "Teaching Assistant ",
        "At ": "at ",
        "Bldg ": "Building ",
        "Bpm ": "BPM ",
        "Brcc ": "BRCC ",
        "Cfo ": "Chief Financial Officer ",
        "Cio ": "Chief Information Officer ",
        "Clin ": "Clinical ",
        "Clncl ": "Clinical ",
        "Cms ": "CMS ",
        "Cns ": "CNS ",
        "Cncr ": "Cancer ",
        "Co ": "Courtesy ",
        "Cog ": "COG ",
        "Communic ": "Communications ",
        "Compar ": "Compare ",
        "Coo ": "Chief Operating Officer ",
        "Copd ": "COPD ",
        "Cpb ": "CPB ",
        "Crd ": "Coordinator ",
        "Cse ": "CSE ",
        "Ctr ": "Center ",
        "Cty ": "County ",
        "Cwp ": "CWP ",
        "Dbl-bl ": "Double-blind ",
        "Dbl-blnd ": "Double-blind ",
        "Dbs ": "DBS ",
        "Dev ": "Development ",
        "Devel ": "Development ",
        "Dist ": "Distinguished ",
        "Dna ": "DNA ",
        "Doh ": "DOH ",
        "Doh/cms ": "DOH/CMS ",
        "Double Blinded ": "Double-blind ",
        "Double-blinded ": "Double-blind ",
        "Dpt-1 ": "DPT-1 ",
        "Dtra0001 ": "DTRA0001 ",
        "Dtra0016 ": "DTRA-0016 ",
        "Educ ": "Education ",
        "Eff/saf ": "Safety and Efficacy ",
        "Eh&S ": "EH&S ",
        "Emer ": "Emeritus ",
        "Emin ": "Eminent ",
        "Enforce ": "Enforcement ",
        "Eng ": "Engineer ",
        "Environ ": "Environmental ",
        "Epr ": "EPR ",
        "Eval ": "Evaluation ",
        "Ext ": "Extension ",
        "Fdot ": "FDOT ",
        "Fdots ": "FDOT ",
        "Fhtcc ": "FHTCC ",
        "Finan ": "Financial ",
        "Fla ": "Florida ",
        "Fllw ": "Follow ",
        "For ": "for ",
        "G-csf ": "G-CSF ",
        "Gen ": "General ",
        "Gis ": "GIS ",
        "Gm-csf ": "GM-CSF ",
        "Grad ": "Graduate ",
        "Hcv ": "HCV ",
        "Hiv ": "HIV ",
        "Hiv-infected ": "HIV-infected ",
        "Hiv/aids ": "HIV/AIDS ",
        "Hlb ": "HLB ",
        "Hlth ": "Health ",
        "Hou ": "Housing ",
        "Hsv-1 ": "HSV-1 ",
        "I/ii ": "I/II ",
        "I/ucrc ": "I/UCRC ",
        "Ica ": "ICA ",
        "Icd ": "ICD ",
        "Ieee ": "IEEE ",
        "Ifas ": "IFAS ",
        "Igf-1 ": "IGF-1 ",
        "Ii ": "II ",
        "Ii/iii ": "II/III ",
        "Iii ": "III ",
        "In ": "in ",
        "Info ": "Information ",
        "Inter-vention ": "Intervention ",
        "Ipa ": "IPA ",
        "Ipm ": "IPM ",
        "Ippd ": "IPPD ",
        "Ips ": "IPS ",
        "It ": "Information Technology ",
        "Iv ": "IV ",
        "Jnt ": "Joint ",
        "Lng ": "Long ",
        "Mccarty ": "McCarty ",
        "Mgmt ": "Management ",
        "Mgr ": "Manager ",
        "Mgt ": "Management ",
        "Mlti ": "Multi ",
        "Mlti-ctr ": "Multicenter ",
        "Mltictr ": "Multicenter ",
        "Mri ": "MRI ",
        "Mstr ": "Master ",
        "Multi-center ": "Multicenter ",
        "Multi-ctr ": "Multicenter ",
        "Nih ": "NIH ",
        "Nmr ": "NMR ",
        "Nsf ": "NSF ",
        "Ne ": "NE ",
        "Nw ": "NW ",
        "Of ": "of ",
        "On ": "on ",
        "Or ": "or ",
        "Open-labeled ": "Open-label ",
        "Opn-lbl ": "Open-label ",
        "Opr ": "Operator ",
        "Phas ": "Phased ",
        "Php ": "PHP ",
        "Phs ": "PHS ",
        "Pk/pd ": "PK/PD ",
        "Pky ": "P. K. Yonge ",
        "Plcb-ctrl ": "Placebo-controlled ",
        "Plcbo ": "Placebo ",
        "Plcbo-ctrl ": "Placebo-controlled ",
        "Postdoc ": "Postdoctoral ",
        "Pract ": "Practitioner ",
        "Pres5 ": "President 5 ",
        "Pres6 ": "President 6 ",
        "Prg ": "Programs ",
        "Prof ": "Professor ",
        "Prog ": "Programmer ",
        "Progs ": "Programs ",
        "Prov ": "Provisional ",
        "Psr ": "PSR ",
        "Radiol ": "Radiology ",
        "Rcv ": "Receiving ",
        "Rdmzd ": "Randomized ",
        "Rep ": "Representative ",
        "Res ": "Research ",
        "Ret ": "Retirement ",
        "Reu ": "REU ",
        "Rna ": "RNA ",
        "Rndmzd ": "Randomized ",
        "Roc-124 ": "ROC-124 ",
        "Rsch ": "Research ",
        "Saf ": "SAF ",
        "Saf/eff ": "Safety and Efficacy ",
        "Sbjcts ": "Subjects ",
        "Sch ": "School ",
        "Se ": "SE ",
        "Ser ": "Service ",
        "Sfwmd ": "SFWMD ",
        "Sle ": "SLE ",
        "Sntc ": "SNTC ",
        "Spec ": "Specialist ",
        "Spnsrd ": "Sponsored ",
        "Spv ": "Supervisor ",
        "Sr ": "Senior ",
        "Stdy ": "Study ",
        "Subj ": "Subject ",
        "Supp ": "Support ",
        "Supt ": "Superintendant ",
        "Supv ": "Supervisor ",
        "Svc ": "Services ",
        "Svcs ": "Services ",
        "Sw ": "SW ",
        "Tch ": "Teaching ",
        "Tech ": "Technician ",
        "Technol ": "Technologist ",
        "Teh ": "the ",
        "The ": "the ",
        "To ": "to ",
        "Trls ": "Trials ",
        "Trm ": "Term ",
        "Tv ": "TV ",
        "Uaa ": "UAA ",
        "Uf ": "UF ",
        "Ufrf ": "UFRF ",
        "Uhf ": "UHF ",
        "Univ ": "University ",
        "Us ": "US ",
        "Usa ": "USA ",
        "Va ": "VA ",
        "Vhf ": "VHF ",
        "Vis ": "Visiting ",
        "Vp ": "Vice President ",
        "Wuft-Fm ": "WUFT-FM "
    }
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

    for abbrev in abbrev_table:
        t = t.replace(abbrev, abbrev_table[abbrev])

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


def get_args():
    """
    Get the args specified by the user.  Arg values are determined:
    1) from hard coded values (see below)
    2) Overridden by values in a specified config file (see below)
    3) Overridden by values on the command line
    :return: args structure as defined by argparser
    """
    import argparse
    import ConfigParser

    program_defaults = {
        'action': 'summarize',
        'defn': 'pump_def.json',
        'inter': '\t',
        'intra': ';',
        'username': 'vivo_root@school.edu',
        'password': 'password',
        'prefix':
        'PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n'
        'PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>\n'
        'PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>\n'
        'PREFIX owl:   <http://www.w3.org/2002/07/owl#>\n'
        'PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>\n'
        'PREFIX bibo: <http://purl.org/ontology/bibo/>\n'
        'PREFIX event: <http://purl.org/NET/c4dm/event.owl#>\n'
        'PREFIX foaf: <http://xmlns.com/foaf/0.1/>\n'
        'PREFIX obo: <http://purl.obolibrary.org/obo/>\n'
        'PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n'
        'PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>\n'
        'PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>\n'
        'PREFIX vivo: <http://vivoweb.org/ontology/core#>\n',
        'rdfprefix': 'pump',
        'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
        'uriprefix': 'http://vivo.school.edu/individual/n',
        'src': 'pump_data.txt',
        'config': 'sv.cfg',
        'verbose': False,
        'nofilters': False
    }

    parser = argparse.ArgumentParser(description="Get or update row and column data from and to VIVO",
                                     epilog="For more info, see http://github.com/mconlon17/vivo-pump")
    parser.add_argument("-a", "--action", help="desired action.  get = get data from VIVO.  update = update VIVO "
                        "data from a spreadsheet. summarize = show def summary. serialize = serial version of the pump",
                        nargs='?')
    parser.add_argument("-d", "--defn", help="name of definition file", nargs="?")
    parser.add_argument("-i", "--inter", help="interfield delimiter", nargs="?")
    parser.add_argument("-j", "--intra", help="intrafield delimiter", nargs="?")
    parser.add_argument("-u", "--username", help="username for API", nargs="?")
    parser.add_argument("-p", "--password", help="password for API", nargs="?")
    parser.add_argument("-q", "--queryuri", help="URI for API", nargs="?")
    parser.add_argument("-r", "--rdfprefix", help="RDF prefix", nargs="?")
    parser.add_argument("-x", "--uriprefix", help="URI prefix", nargs="?")
    parser.add_argument("-s", "--src", help="name of source file containing data to be updated in VIVO", nargs='?')
    parser.add_argument("-c", "--config", help="name of file containing config data.  Config data overrides program "
                        "defaults. Command line overrides config file values", nargs='?')
    parser.add_argument("-v", "--verbose", action="store_true", help="write verbose processing messages to the log")
    parser.add_argument("-n", "--nofilters", action="store_true", help="turn off filters")
    args = parser.parse_args()

    if args.config is None:
        args.config = program_defaults['config']

    #   Config file values overwrite program defaults

    config = ConfigParser.ConfigParser()
    config.read(args.config)  # Read the config file from the config filename specified in the command line args
    for section in config.sections():
        for name, val in config.items(section):
            program_defaults[name] = val

    #   Non null command line values overwrite the config file values

    for name, val in vars(args).items():
        if val is not None:
            program_defaults[name] = val

    #   Put the final values back in args

    for name, val in program_defaults.items():
        if val == 'tab':
            val = '\t'
        vars(args)[name] = val

    return args


def get_parms():
    """
    Use get args to get the args, and return a dictionary of the args ready for use in pump software
    :return: dict: parms
    """
    parms = {}
    args = get_args()
    for name, val in vars(args).items():
        if val is not None:
            parms[name] = val
    return parms


def make_get_query(update_def):
    """
    Given an update_def, return the sparql query needed to produce a spreadsheet of the data to be managed.
    See do_get
    :return: a sparql query string
    """

    front_query = 'SELECT ?uri ?' + ' ?'.join(update_def['column_defs'].keys()) + '\nWHERE {\n    ' + \
                  update_def['entity_def']['entity_sparql'] + '\n'

    # Fake recursion here to depth 3.  Could be replaced by real recursion to arbitrary path length

    middle_query = ""
    for name, path in update_def['column_defs'].items():
        middle_query += '    OPTIONAL {  ?uri <' + str(path[0]['predicate']['ref']) + '> ?'
        if len(path) == 1:
            middle_query += name + ' . ' + add_qualifiers(path) + ' }\n'
        else:
            middle_query += path[0]['object']['name'] + ' . ?' + \
                path[0]['object']['name'] + ' <' + str(path[1]['predicate']['ref']) + '> ?'
            if len(path) == 2:
                middle_query += name + ' . ' + add_qualifiers(path) + ' }\n'
            else:
                middle_query += path[1]['object']['name'] + ' . ?' + \
                    path[1]['object']['name'] + ' <' + str(path[2]['predicate']['ref']) + '> ?'
                if len(path) == 3:
                    middle_query += name + ' . ' + add_qualifiers(path) + ' }\n'
                else:
                    raise PathLengthException('Path length >3 not supported in do_get')

    back_query = '}\nORDER BY ?' + update_def['entity_def']['order_by']
    return front_query + middle_query + back_query


def unique_path(path):
    """
    Given a path, determine if all its elements are single-valued predicates.  If so, the path is unique,
    regardless of length.  If any one of the steps in the path has a non single-valued predicated, the path is not
    unique.
    :param path: a definition path
    :return: True if path is unique
    :rtype: boolean
    """
    unique = True
    for elem in path:
        if not elem['predicate']['single']:
            unique = False
            break
    return unique


def make_get_data(update_def, result_set):
    """
    Given a query result set, produce a data structure with one element per uri and column values collected
    into lists.  If VIVO has multiple values for a path defined to be unique, print a WARNING to the log and
    return the first value found in the data, ignoring the rest
    :param result_set: SPARQL result set
    :return: dictionary
    :rtype: dict
    """
    data = {}

    for binding in result_set['results']['bindings']:
        uri = str(binding['uri']['value'])
        if uri not in data:
            data[uri] = {}
        for name in ['uri'] + update_def['column_defs'].keys():
            if name in binding:
                if name in data[uri]:
                    data[uri][name].add(binding[name]['value'])
                else:
                    data[uri][name] = {binding[name]['value']}
    return data


def prepare_column_values(update_string, intra, step_def, enum, row, column_name):
    """
    Given the string of data from the update file, the step definition, the row and column name of the
    update_string in the update file, enumerations and filters, prepare the column values and return them
    as a list of strings
    :return: column_values a list of strings
    :rtype: list[str]
    """

    if step_def['predicate']['single']:
        column_values = [update_string.strip()]
    else:
        column_values = update_string.split(intra)
        if 'include' in step_def['predicate']:
            column_values += step_def['predicate']['include']
        for i in range(len(column_values)):
            column_values[i] = column_values[i].strip()


    # Check column values for consistency with single and multi-value attributes

    if step_def['predicate']['single'] and len(column_values) > 1:
        raise InvalidDataException(str(row) + str(column_name) +
                                   'Predicate is single-valued, multiple values in source.')
    while '' in column_values:
        column_values.remove('')
    if 'None' in column_values and len(column_values) > 1:
        raise InvalidDataException(str(row) + str(column_name) +
                                   'None value in multi-valued predicate set')

    # Handle enumerations

    if 'enum' in step_def['object']:
        for i in range(len(column_values)):
            try:
                column_values[i] = enum[step_def['object']['enum']]['update'][column_values[i]]
            except KeyError:
                print "ERROR: ", column_values[i], "not found in enumeration.  Blank value substituted."
                column_values[i] = ''

    return column_values


def get_step_triples(update_graph, uri, step_def, query_parms, debug):
    """
    Return the triples matching the criteria defined in the current step of an update
    :param update_graph: the update graph
    :param uri: uri of the entity currently the subject of an update
    :param step_def: step definition from update_def
    :return:  Graph containing one or more triples that match the criteria for the step
    """
    from rdflib import Graph

    if 'qualifier' not in step_def['object']:
        g = update_graph.triples((uri, step_def['predicate']['ref'], None))
    else:
        if 'name' in step_def['object']:
            q = 'select (?' + step_def['object']['name'] + ' as ?o) where { <' + str(uri) + '> <' + \
                str(step_def['predicate']['ref']) + '> ?' + step_def['object']['name'] + ' .\n' + \
                add_qualifiers([step_def]) + ' }\n'
        else:
            q = 'select ?o where { <' + str(uri) + '> <' + \
                str(step_def['predicate']['ref']) + '> ?o .\n' + \
                add_qualifiers([step_def]) + ' }\n'
        if debug:
            print "\nStep Triples Query\n", q
        result_set = vivo_query(q, query_parms, debug)
        g = Graph()
        for binding in result_set['results']['bindings']:
            o = make_rdf_term(binding['o'])
            g.add((uri, step_def['predicate']['ref'], o))
        if debug:
            print "Step Triples\n", g.serialize(format='nt')
    return g


def load_enum(update_def):
    """
    Find all enumerations in the update_def. for each, read the corresponding enum file and build the corresponding
    pair of enum dictionaries.

    The two columns in the tab delimited input file must be called "short" and "vivo".  "vivo" is the value to put in
    vivo (update) or get from vivo.  short is the human usable short form.

    The input file name appears as the 'enum' value in update_def

    :return enumeration structure.  Pairs of dictionaries, one pair for each enumeration.  short -> vivo, vivo -> short
    """
    # import os
    enum = {}
    for path in update_def['column_defs'].values():
        for step in path:
            if 'object' in step and 'enum' in step['object']:
                enum_filename = step['object']['enum']
                enum_name = enum_filename
                # enum_name = os.path.splitext(os.path.split(enum_filename)[1])[0]
                if enum_name not in enum:
                    enum[enum_name] = {}
                    enum[enum_name]['get'] = {}
                    enum[enum_name]['update'] = {}
                    enum_data = read_csv(enum_filename, delimiter='\t')
                    for enum_datum in enum_data.values():
                        enum[enum_name]['get'][enum_datum['vivo']] = enum_datum['short']
                        enum[enum_name]['update'][enum_datum['short']] = enum_datum['vivo']
    return enum
