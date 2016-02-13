#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vivopump -- module of helper functions for the pump
"""

import sys
import csv
import string
import random
import logging

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2016 Michael Conlon"
__license__ = "New BSD license"
__version__ = "0.8.7"

logger = logging.getLogger(__name__)


class DefNotFoundException(Exception):
    """
    Raise this exception when update definition fle is not found
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidDefException(Exception):
    """
    Raise this exception when update definition contains values that can not be processed
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidSourceException(Exception):
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
    logger.debug("loader returns {} rows".format(len(data)))
    return data


def write_csv_fp(fp, data, delimiter='|'):
    """
    Write a CSV to a file pointer.  Used to support stdout.
    :param fp: File pointer.  Could be stdout.
    :param data: data to be written
    :param delimiter: field delimiter for output
    :return:
    """
    assert(len(data.keys()) > 0)

    # create a list of var_names from the first row
    var_names = data[data.keys()[0]].keys()
    fp.write(delimiter.join(var_names) + '\n')

    for key in sorted(data.keys()):
        fp.write(delimiter.join([data[key][x] for x in var_names]) + '\n')


def write_csv(filename, data, delimiter='|'):
    """
    Given a filename, a data structure as produced by read_csv and an optional
    delimiter, write a file that can be read by read_csv

    The data structure is a dictionary keyed by an integer of "row numbers"
    preserving the natural order of the data.  Each element is in turn a
    dictionary of name value pairs.  All values are strings.

    :param filename: name of file to write
    :param data: data structure to be written to the file
    :param delimiter: field delimiter.  Popular choices are '|', '\t' and ','
    :return:
    """
    with open(filename, 'w') as f:
        f.write(delimiter.join(data[data.keys()[0]].keys()) + '\n')
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
    Query VIVO and return a list of all the journals.
    @see uf_examples/publications/filters/journal_match_filter.py

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
    Query VIVO and return a list of all the ccn found in VIVO.
    @see uf_examples/courses/merge_filter.py

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

    query = "select ?uri ?sponsorid where {?uri a vivo:FundingOrganization . ?uri ufVivo:sponsorID ?sponsorid .}"
    a = vivo_query(query, parms)
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


def read_update_def(filename, prefix):
    """
    Read an update_def in JSON format, from a file
    :param filename: name of file to read
    :param prefix: text prefix for sparql queries
    :rtype: dict
    :return: JSON-like object from file, replacing all URI strings with URIRef objects
    """

    def make_prefix_dict(prefix_text):
        """
        Given prefix text, return a prefix dictionary with tags as keys and url strings as values
        :param prefix_text:
        :return: dictionary
        :rtype: dict
        """
        prefix_dictionary = {}
        prefix_list = prefix_text.split()
        for i in range(len(prefix_list) - 2):
            if prefix_list[i].upper() == "PREFIX":
                prefix_dictionary[prefix_list[i + 1]] = prefix_list[i + 2].replace('<', '').replace('>', '')

        return prefix_dictionary

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

    def fixit(current_object, prefix_dictionary):
        """
        Read the def data structure and replace all string URIs with URIRef entities
        :param current_object: the piece of the data structure to be fixed
        :return current_object: the piece repaired in place
        """
        from rdflib import URIRef
        if isinstance(current_object, dict):
            for k in current_object.keys():
                current_object[k] = fixit(current_object[k], prefix_dictionary)
        elif isinstance(current_object, list):
            for i in range(0, len(current_object)):
                current_object[i] = fixit(current_object[i], prefix_dictionary)
        elif isinstance(current_object, basestring):
            if current_object.startswith("http://"):
                current_object = URIRef(current_object)
            elif current_object.startswith("xsd:"):
                current_object = cast_to_rdflib(current_object)
            elif ':' in current_object:
                k = current_object.find(':')
                tag = str(current_object[0:k + 1])
                if tag in prefix_dictionary:
                    current_object = URIRef(str(current_object).replace(tag, prefix_dictionary[tag]))
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
        col_names = a['column_defs'].keys()

        #   Test that each closure_def name can be found in the column_def names

        for name in a.get('closure_defs', {}).keys():
            if name not in col_names:
                raise InvalidDefException(name + 'in closure_def, not in column_def.')

        #   Test for agreement between closure_def and column_def last step object type and datatype

        if 'closure_defs' in a:
            for name in a.get('closure_defs').keys():
                col_object = a['column_defs'][name][-1]['object']  # last object in the column_def
                clo_object = a['closure_defs'][name][-1]['object']  # last object in the closure_def
                if col_object.get('dataype', '') == clo_object.get('datatype', '') and \
                   col_object.get('type', '') == clo_object.get('type', ''):
                    continue
                else:
                    raise InvalidDefException(name + ' has inconsistent datatype or type in closure')

        #   Test for paths having more than one multiple predicate

        for name in col_names:
            multiple = 0
            for step in a['column_defs'][name]:
                if step['predicate']['single'] == False:
                    multiple += 1
                    if multiple > 1:
                        raise InvalidDefException(name + ' has more than one multiple predicate')

        #   Test for presence of required boolean value

        for name in col_names:
            for step in a['column_defs'][name]:
                if step['predicate']['single'] == 'boolean' and 'value' not in step['object']:
                    raise InvalidDefException(name + 'is boolean with no value')
        return None

    def add_object_names_and_step_attributes(a):
        """
        handed an update_def structure a, return an improved structure b in which each object has a generated name
        attribute based on the column_def or closure_def name
        Assign multiple to each object.  Object is multiple if any preceding predicate is not single
        """
        b = dict(a)
        for name, path in b['column_defs'].items():
            multiple = False
            for i in range(len(path)):
                multiple = multiple or (b['column_defs'][name][i]['predicate']['single'] == False)
                b['column_defs'][name][i]['closure'] = False
                b['column_defs'][name][i]['column_name'] = name
                b['column_defs'][name][i]['object']['multiple'] = multiple
                if i==len(path) - 1:
                    b['column_defs'][name][i]['object']['name'] = name
                    b['column_defs'][name][i]['last'] = True
                else:
                    b['column_defs'][name][i]['object']['name'] = name + '_' + str(len(path) - i - 1)
                    b['column_defs'][name][i]['last'] = False
        if 'closure_defs' in b:
            for name, path in b['closure_defs'].items():
                multiple = False
                for i in range(len(path)):
                    multiple = multiple or (b['closure_defs'][name][i]['predicate']['single'] == False)
                    b['closure_defs'][name][i]['closure'] = True
                    b['closure_defs'][name][i]['column_name'] = name
                    b['closure_defs'][name][i]['object']['multiple'] = multiple
                    if i==len(path) - 1:
                        b['closure_defs'][name][i]['object']['name'] = name
                        b['closure_defs'][name][i]['last'] = True
                    else:
                        b['closure_defs'][name][i]['object']['name'] = name + '_' + str(len(path) - i - 1)
                        b['closure_defs'][name][i]['last'] = False
        return b

    import json
    with open(filename, "r") as my_file:
        data = my_file.read()
        prefix_dict = make_prefix_dict(prefix)
        update_def = fixit(json.loads(data), prefix_dict)
        update_def = add_order(update_def, data)
        update_def = add_object_names_and_step_attributes(update_def)
        validate_update_def(update_def)
    return update_def


def add_qualifiers(input_path):
    """
    Given an update_def input_path, generate the SPARQL fragment to express the qualifiers in the path, if any
    :param input_path:
    :return: qualifer SPARQL string
    """
    return ' '.join([x['object'].get('qualifier', '') for x in input_path])


def gather_types(input_step, varname):
    """
    Given and input step, return a SPARQL fragment to gather the types for the step
    :param input_step:
    :return: SPARQL fragment as string
    """
    if not input_step['object']['literal']:
        return ' ?' + input_step['object']['name'] + ' a ?' + varname + ' . '
    else:
        return ''


def make_update_query(entity_sparql, path):
    """
    Given a path from an update_def data structure, generate the query needed to pull the triples from VIVO that might
    be updated.  Here's what the queries look like (psuedo code) by path length

    Path length 1 example:

            select ?uri (vivo:subOrganizationWithin as ?p) (?column_name as ?o)
            where {
                ... entity sparql goes here ...
                ?uri vivo:subOrganizationWithin ?column_name .  # ?uri ?p ?o
            }

    Path Length 2 example:

            select ?uri (vivo:webpage as ?p1) (?column_name_1 as ?o1) (vivo:linkURI as ?p) (?column_name as ?o)
            where {
                ... entity sparql goes here ...
                ?uri vivo:webpage ?column_name_1 .           # ?uri ?p1 ?o1
                ?column_name_1 vivo:linkURI ?column_name .   # ?o1 ?p ?o
            }

    Path length 3 example:

            select ?uri (vivo:dateTimeInterval as ?p2) (?column_name_2 as ?o2) (vivo:end as ?p1)
                                                            (?column_name_1 as ?o1) (vivo:dateTime as ?p)
                                                            (?column_name as ?o)
            where {
                ... entity sparql goes here ...
                ?uri vivo:dateTimeInterval ?column_name_2 .  # ?uri ?p2 ?o2
                ?column_name_2 vivo:end ?column_name_1 .     # ?o2 ?p1 ?o1
                ?column_name_1 vivo:dateTime ?column_name .  # ?o1 ?p ?o
            }

    :return: a sparql query string
    """
    query = ""
    if len(path) == 1:
        query = 'select ?uri (<' + str(path[0]['predicate']['ref']) + '> as ?p) (?' + path[0]['object']['name'] + \
                ' as ?o) ?t\n' + \
                '    where { ' + entity_sparql + '\n    ?uri <' + str(path[0]['predicate']['ref']) + '> ?' + \
                path[0]['object']['name'] + \
                ' . ' + gather_types(path[0], 't') + add_qualifiers(path) + ' \n}'
    elif len(path) == 2:
        query = 'select ?uri (<' + str(path[0]['predicate']['ref']) + '> as ?p1) ' + \
                '(?' + path[0]['object']['name'] + ' as ?o1) ?t1 (<' + \
                str(path[1]['predicate']['ref']) + '> as ?p) (?' + path[1]['object']['name'] + ' as ?o) ?t\n' + \
                '    where { ' + entity_sparql + '\n    ?uri <' + str(path[0]['predicate']['ref']) + '> ?' + \
                path[0]['object']['name'] + ' . ' + gather_types(path[0], 't1') + '?' + \
                path[0]['object']['name'] + ' <' + str(path[1]['predicate']['ref']) + '> ?' + \
                path[1]['object']['name'] + ' . ' + gather_types(path[1], 't') + add_qualifiers(path) + ' \n}'
    elif len(path) == 3:
        query = 'select ?uri (<' + str(path[0]['predicate']['ref']) + '> as ?p2) ' + \
                '(?' + path[0]['object']['name'] + ' as ?o2) ?t2 (<' + str(path[1]['predicate']['ref']) + \
                '> as ?p1) (?' + path[1]['object']['name'] + ' as ?o1) ?t1 (<' + str(path[2]['predicate']['ref']) + \
                '> as ?p) (?' + path[2]['object']['name'] + ' as ?o)  ?t\n' + \
                'where { ' + entity_sparql + '\n    ?uri <' + \
                str(path[0]['predicate']['ref']) + '> ?' + path[0]['object']['name'] + ' . ' + \
                gather_types(path[0], 't2') + ' ?' + \
                path[0]['object']['name'] + ' <' + str(path[1]['predicate']['ref']) + '> ?' + \
                path[1]['object']['name'] + ' . ' + gather_types(path[1], 't1') + ' ?' + \
                path[1]['object']['name'] + ' <' + \
                str(path[2]['predicate']['ref']) + '> ?' + path[2]['object']['name'] + ' . ' + \
                gather_types(path[2], 't') + add_qualifiers(path) + ' \n}'
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


def get_graph(update_def, query_parms):
    """
    Given the update def, get a graph from VIVO of the triples eligible for updating
    :return: graph of triples
    """

    from rdflib import Graph, URIRef, RDF

    a = Graph()
    entity_query = 'select ?uri (<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> as ?p) (<' + \
        str(update_def['entity_def']['type']) + '> as ?o)\nwhere {\n    ' + \
        update_def['entity_def']['entity_sparql'] + '\n}'
    result = vivo_query(entity_query, query_parms)
    for row in result['results']['bindings']:
        s = URIRef(row['uri']['value'])
        p = URIRef(row['p']['value'])
        o = make_rdf_term(row['o'])
        a.add((s, p, o))
    for column_name, path in update_def['column_defs'].items() + \
            update_def.get('closure_defs', {}).items():
        update_query = make_update_query(update_def['entity_def']['entity_sparql'], path)
        if len(update_query) == 0:
            continue
        result = vivo_query(update_query, query_parms)
        for row in result['results']['bindings']:
            if 'p2' in row and 'o2' in row:
                uri = URIRef(row['uri']['value'])
                p2 = URIRef(row['p2']['value'])
                o2 = make_rdf_term(row['o2'])
                a.add((uri, p2, o2))
                if 't2' in row:
                    a.add((o2, RDF.type, make_rdf_term(row['t2'])))
                p1 = URIRef(row['p1']['value'])
                o1 = make_rdf_term(row['o1'])
                a.add((o2, p1, o1))
                if 't1' in row:
                    a.add((o1, RDF.type, make_rdf_term(row['t1'])))
                p = URIRef(row['p']['value'])
                o = make_rdf_term(row['o'])
                a.add((o1, p, o))
                if 't' in row:
                    a.add((o, RDF.type, make_rdf_term(row['t'])))
            elif 'p1' in row and 'o1' in row:
                uri = URIRef(row['uri']['value'])
                p1 = URIRef(row['p1']['value'])
                o1 = make_rdf_term(row['o1'])
                a.add((uri, p1, o1))
                if 't1' in row:
                    a.add((o1, RDF.type, make_rdf_term(row['t1'])))
                p = URIRef(row['p']['value'])
                o = make_rdf_term(row['o'])
                a.add((o1, p, o))
                if 't' in row:
                    a.add((o, RDF.type, make_rdf_term(row['t'])))
            elif 'p' in row and 'o' in row:
                uri = URIRef(row['uri']['value'])
                p = URIRef(row['p']['value'])
                o = make_rdf_term(row['o'])
                a.add((uri, p, o))
                if 't' in row:
                    a.add((o, RDF.type, make_rdf_term(row['t'])))

        logger.debug(u"Triples in original graph {}".format(len(a)))
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


def vivo_query(query, parms):
    """
    A new VIVO query function using SPARQLWrapper.  Tested with Stardog, UF VIVO and Dbpedia
    :param query: SPARQL query.  VIVO PREFIX will be added
    :param parms: dictionary with query parms:  queryuri, username and password
    :return: result object, typically JSON
    :rtype: dict
    """
    from SPARQLWrapper import SPARQLWrapper, JSON

    logger.debug(u"in vivo_query\n{}".format(parms))
    sparql = SPARQLWrapper(parms['queryuri'])
    new_query = parms['prefix'] + '\n' + query
    sparql.setQuery(new_query)
    logger.debug(new_query)
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
    Given a month string and a year string from publisher data, parse apart the month, day and year and create
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
    1. from hard coded values (see below)
    2. Overridden by values in a specified config file (see below)
    3. Overridden by values on the command line

    Set the logging level based on args

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
        'verbose': logging.WARNING,
        'debug': logging.WARNING,
        'nofilters': False
    }

    parser = argparse.ArgumentParser(description="Get or update row and column data from and to VIVO",
                                     epilog="For more info, see http://github.com/mconlon17/vivo-pump")
    parser.add_argument("-a", "--action", help="desired action.  get = get data from VIVO.  update = update VIVO "
                        "data from a spreadsheet. summarize = show def summary. serialize = serial version of the pump"
                        ". test = test pump configuration.",
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
    parser.add_argument("-v", "--verbose", action="store_const", dest='loglevel', const=logging.INFO,
                        help="write informational messages to the log")
    parser.add_argument("-b", "--debug", action="store_const", dest='loglevel', const=logging.DEBUG,
                        default=logging.WARNING, help="write debugging messages to the log")
    parser.add_argument("-n", "--nofilters", action="store_true", help="turn off filters")
    args = parser.parse_args()

    if args.config is None:
        args.config = program_defaults['config']
        logger.debug(u"No config file specified -- using hardcoded defaults")
    else:
        logger.debug(u"Reading config file: {}".format(args.config))

    # Read the config parameters from the file specified in the command line

    config = ConfigParser.ConfigParser()
    try:
        config.read(args.config)
    except IOError:
        logger.error(u"Config file {} not found.".format(args.config))
        sys.exit(1)

    # Config file values overwrite program defaults

    for section in config.sections():
        for name, val in config.items(section):
            program_defaults[name] = val
            if 'prefix' != name:
                logger.debug(u"Param {} = {}".format(name, val))

    # Non null command line values overwrite the config file values

    for name, val in vars(args).items():
        if val is not None:
            program_defaults[name] = val

    # Put the final values back in args

    for name, val in program_defaults.items():
        if val == 'tab':
            val = '\t'
        vars(args)[name] = val

    # Set the level of logging if verbose and/or debug args were used

    if args.loglevel:
        logging.basicConfig(level=args.loglevel)

    return args


def get_parms():
    """
    Use get_args to get the args, and return a dictionary of the args ready for
    use in pump software.
    @see get_args()

    :return: dict: parms
    """
    parms = {}
    args = get_args()
    for name, val in vars(args).items():
        if val is not None:
            parms[name] = val
    return parms


def add_type_restriction(step):
    """
    for a given step, look for object type and construct a SPARQL fragement to restrict the graph
    to objects of the type. If the object does not have a type restriction, return an empty string.
    :param step: The step for which an object restriction is requested
    :return: the SPARQL fragement for thr restriction, or an empty string if no type is specified
    """
    if 'type' in step['object']:
        return '?' + step['object']['name'] + ' a <' + str(step['object']['type']) + '> . '
    else:
        return ""


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
            middle_query += name + ' . ' + add_type_restriction(path[0]) + add_qualifiers(path) + ' }\n'
        else:
            middle_query += path[0]['object']['name'] + ' . ' + add_type_restriction(path[0]) + '?' + \
                path[0]['object']['name'] + ' <' + str(path[1]['predicate']['ref']) + '> ?'
            if len(path) == 2:
                middle_query += name + ' . ' + add_type_restriction(path[1]) + add_qualifiers(path) + ' }\n'
            else:
                middle_query += path[1]['object']['name'] + ' . ' + add_type_restriction(path[1]) + '?' + \
                    path[1]['object']['name'] + ' <' + str(path[2]['predicate']['ref']) + '> ?'
                if len(path) == 3:
                    middle_query += name + ' . ' + add_type_restriction(path[2]) + add_qualifiers(path) + ' }\n'
                else:
                    raise PathLengthException('Path length >3 not supported in do_get')
    if 'order_by' in update_def['entity_def']:
        back_query = '}\nORDER BY ?' + update_def['entity_def']['order_by']
    else:
        back_query = '}\n'
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
        if elem['predicate']['single'] != True:
            unique = False
            break
    return unique


def make_get_data(update_def, result_set):
    """
    Given a query result set, produce a dictionary keyed by uri with values of dictionaries keyed by column
    names.  Where columns have multiple values, create sets of values.
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
            if name != 'uri':
                last_step = update_def['column_defs'][name][len(update_def['column_defs'][name]) - 1]
            if name != 'uri' and last_step['predicate']['single'] == 'boolean':
                if name in binding and (str(last_step['object']['value']) == binding[name]['value']):
                    data[uri][name] = '1'
                elif name not in data[uri]:
                    data[uri][name] = '0'
            else:
                if name in binding:
                    if name in data[uri]:
                        data[uri][name].add(binding[name]['value'])
                    else:
                        data[uri][name] = {binding[name]['value']}
    return data


def make_rdf_term_from_source(value, step):
    """
    Given a text string value and a step definition, return the rdflib term as defined by the step def
    :param: value: string from source
    :param: step: step definition from update_def
    :return: rdf_term: an rdf_term from rdflib -- either Literal or URIRef
    """
    from rdflib import Literal, URIRef
    if step["object"]["literal"]:
        datatype = step["object"].get('datatype', None)
        if datatype is not None and datatype[:4] == 'xsd:':
            datatype = datatype.replace('xsd:', 'http://www.w3.org/2001/XMLSchema#')
        rdf_term = Literal(value, datatype=datatype, lang=step["object"].get('lang', None))
    else:
        rdf_term = URIRef(value)
    return rdf_term


def prepare_column_values(update_string, intra, step_def, enum, row, column_name):
    """
    Given the string of data from the update file, the step definition, the row and column name of the
    update_string in the update file, enumerations and filters, prepare the column values and return them
    as a list of rdflib terms

    :return: column_values a list of rdflib terms
    :rtype: list[str]
    """

    #   Three cases: boolean, single valued and multiple valued

    if step_def['predicate']['single'] == 'boolean':
        update_string = update_string.strip()
        if update_string == '':
            column_values = ['']
        elif update_string == '0' or update_string == 'None' or update_string.lower() == 'false' or \
                update_string.lower() == 'n' or update_string.lower() == 'no':
            column_values = ['0']
        else:
            column_values = ['1']

    elif not step_def['object']['multiple']:
        column_values = [update_string.strip()]
    else:
        column_values = update_string.split(intra)
        if 'include' in step_def['predicate']:
            column_values += step_def['predicate']['include']
        for i in range(len(column_values)):
            column_values[i] = column_values[i].strip()

    # Check column values for consistency with single and multi-value paths

    if step_def['object']['multiple'] != True and len(column_values) > 1:
        raise InvalidSourceException(str(row) + str(column_name) +
                                     'Path is single-valued, multiple values in source.')
    while '' in column_values:
        column_values.remove('')

    if 'None' in column_values and len(column_values) > 1:
        raise InvalidSourceException(str(row) + str(column_name) +
                                     'None value in multi-valued predicate set')

    # Handle enumerations

    if 'enum' in step_def['object']:
        for i in range(len(column_values)):
            try:
                column_values[i] = enum[step_def['object']['enum']]['update'][column_values[i]]
            except KeyError:
                logger.error(u"{} not found in enumeration.  Blank value substituted.".format(column_values[i]))
                column_values[i] = ''

    # Convert to rdflib terms

    column_terms = [make_rdf_term_from_source(column_value, step_def) for column_value in column_values]

    return column_terms


def load_enum(update_def):
    """
    Find all enumerations in the update_def. for each, read the corresponding enum file and build the corresponding
    pair of enum dictionaries.

    The two columns in the tab delimited input file must be called "short" and "vivo".  "vivo" is the value to put in
    vivo (update) or get from vivo.  short is the human usable short form.

    The input file name appears as the 'enum' value in update_def

    :return enumeration structure.  Pairs of dictionaries, one pair for each enumeration.  short -> vivo, vivo -> short
    """
    enum = {}
    for path in update_def['column_defs'].values():
        for step in path:
            if 'object' in step and 'enum' in step['object']:
                enum_name = step['object']['enum']
                if enum_name not in enum:
                    enum[enum_name] = {}
                    enum[enum_name]['get'] = {}
                    enum[enum_name]['update'] = {}
                    enum_data = read_csv(enum_name, delimiter='\t')
                    for enum_datum in enum_data.values():
                        try:
                            enum[enum_name]['get'][enum_datum['vivo']] = enum_datum['short']
                        except KeyError:
                            logger.error(
                                u"Enumeration {} does not have required columns named short and vivo".format(enum_name))
                            raise KeyError
                        enum[enum_name]['update'][enum_datum['short']] = enum_datum['vivo']
    return enum


def create_enum(filename, query, parms, trim=0, skip=0):
    """
    Given, query, parms and a filename, execute the query and write the enum into the file
    :param: filename: name of the file to contain the enumeration
    :param: query: the query to be used to create the columns for the enumeration
    :param: parms: dictionary of VIVO SPARQL API parameters
    :param: trim:  If 0, no trim.  If k, return the first k characters as a trimmed value for short
    :param: skip: If 0, no skip.  If k, skip the first k characters as a trimmed value for short
    :return: None
    """
    import codecs
    data = vivo_query(query, parms)
    outfile = codecs.open(filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')
    outfile.write("short\tvivo\n")
    for item in data['results']['bindings']:
        if trim == 0 and skip==0:
            outfile.write(item["short"]["value"] + "\t" + item["vivo"]["value"] + "\n")
        elif trim != 0 and skip == 0:
            outfile.write(item["short"]["value"][:trim] + "\t" + item["vivo"]["value"] + "\n")
        elif trim == 0 and skip != 0:
            outfile.write(item["short"]["value"][skip:] + "\t" + item["vivo"]["value"] + "\n")
        else:
            outfile.write(item["short"]["value"][skip:-trim] + "\t" + item["vivo"]["value"] + "\n")
    outfile.close()