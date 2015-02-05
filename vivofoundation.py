#!/usr/bin/env/python
""" vivofoundation.py -- A library of useful things for working with VIVO

    See CHANGELOG for a running account of the changes to vivofoundation
"""
# TODO PEP-8 improvements throughout
# TODO Repair reference errors
# TODO: Repurpose and rename this file as the helper file for the pump

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2014, University of Florida"
__license__ = "BSD 3-Clause license"
__version__ = "2.03"

concept_dictionary = {}

VIVO_URI_PREFIX = "http://vivo.ufl.edu/individual/"
VIVO_QUERY_URI = "http://sparql.vivo.ufl.edu/VIVO/sparql"  # UF Production

import urllib
import json
import random
import string
from datetime import datetime
import time
import csv
import tempita


class UnknownDateTimePrecision(Exception):
    """
    Functions that accept a DateTime Precision will throw this exception if the
    provided value is not one of the known VIVO DateTime precisions.
    """
    pass


def comma_space(s):
    """
    insert a space after every comma in s unless s ends in a comma
    """
    # TODO write test function
    k = s.find(',')
    if -1 < k < len(s) - 1 and s[k+1] != " ":
        s = s[0:k] + ', ' + comma_space(s[k+1:])
    return s


def make_datetime_rdf(value, title):
    """
    Given a bibtex publication value, create the RDF for a datetime object
    expressing the date of publication
    """
    datetime_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#DateTimeValue"/>
        <core:dateTimePrecision rdf:resource=vivo:yearMonthPrecision"/>
        <core:dateTime>{{pub_datetime}}</core:dateTime>
        <ufVivo:harvestedBy>Python Pubs version 1.3</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)
    uri = get_vivo_uri()
    pub_datetime = make_pub_datetime(value)
    harvest_datetime = make_harvest_datetime()
    rdf = "<!-- Timestamp RDF for " + title + "-->"
    rdf = rdf + datetime_template.substitute(uri=uri,\
        pub_datetime=pub_datetime, harvest_datetime=harvest_datetime)
    return [rdf, uri]


def add_dtv(dtv):
    """
    Given values for a date time value, generate the RDF necessary to add the
    datetime value to VIVO

    date_time           datetime value
    datetime_precision  text string in tag format of VIVO date time precision,
                        example 'vivo:yearMonthDayPrecision'
    """
    # TODO write test function
    ardf = ""
    if 'date_time' not in dtv or 'datetime_precision' not in dtv or \
       dtv['date_time'] is None:
        return ["", None]
    else:
        dtv_uri = get_vivo_uri()
        dtv_string = dtv['date_time'].isoformat()
        ardf = ardf + assert_resource_property(dtv_uri,
            'rdf:type', untag_predicate('vivo:DateTimeValue'))
        ardf = ardf + assert_data_property(dtv_uri,
            'vivo:dateTime', dtv_string)
        ardf = ardf + assert_resource_property(dtv_uri,
            'vivo:dateTimePrecision', untag_predicate(dtv['datetime_precision']))
        return [ardf, dtv_uri]


def add_dti(dti):
    """
    Given date time interval attributes, return rdf to create the date time
    interval

    start   start date as a datetime or None or not present
    end     start date as a datetime or None or not present

    Assumes yearMonthDayPrecision for start and end
    """
    # TODO write test function
    ardf = ""
        
    dtv = {'date_time' : dti.get('start',None),
           'datetime_precision': 'vivo:yearMonthDayPrecision'}
    [add, start_uri] = add_dtv(dtv)
    ardf = ardf + add
    dtv = {'date_time' : dti.get('end',None),
           'datetime_precision': 'vivo:yearMonthDayPrecision'}
    [add, end_uri] = add_dtv(dtv)
    ardf = ardf + add
    if start_uri is None and end_uri is None:
        return ["", None]
    else:
        dti_uri = get_vivo_uri()
        ardf = ardf + assert_resource_property(dti_uri,
                'rdf:type', untag_predicate('vivo:DateTimeInterval'))
        if start_uri is not None:
            ardf = ardf + assert_resource_property(dti_uri,
                    'vivo:start', start_uri)
        if end_uri is not None:
            ardf = ardf + assert_resource_property(dti_uri,
                    'rdf:end', end_uri)
        return [ardf, dti_uri]


def update_entity(vivo_entity, source_entity, key_table):
    """
    Given a VIVO entity and a source entity, go through the elements
    in the key_table and update VIVO as needed.

    Four actions are supported:

    literal -- single valued literal.  Such as an entity label
    resource -- single valued reference to another object.  Such as the
        publisher of a journal
    literal_list -- a list of literal values.  Such as phone numbers for
        a person
    resource_list -- a list of references to other objects.  Such as a
        a list of references to concepts for a paper

    If the key is not found in the source_entity, then no change is made
    to VIVO.  If key is found in the source entity, and the value is None
    or an empty list, the corresponding change is made to VIVO.
    """
    # TODO write test function
    entity_uri = vivo_entity['uri']
    ardf = ""
    srdf = ""
    for key in key_table.keys():
        action = key_table[key]['action']
        if action == 'literal':
            if key in vivo_entity:
                vivo_value = vivo_entity[key]
            else:
                vivo_value = None
            if key in source_entity:
                source_value = source_entity[key]
            else:
                continue # if key is not in source, do nothing
            [add, sub] = update_data_property(entity_uri,
                key_table[key]['predicate'], vivo_value, source_value)
            ardf = ardf + add
            srdf = srdf + sub
        elif action == 'resource':
            if key in vivo_entity:
                vivo_value = vivo_entity[key]
            else:
                vivo_value = None
            if key in source_entity:
                source_value = source_entity[key]
            else:
                continue # if key is not in source, do nothing
            [add, sub] = update_resource_property(entity_uri,
                key_table[key]['predicate'], vivo_value, source_value)
            ardf = ardf + add
            srdf = srdf + sub
        elif action == 'literal_list':
            if key not in source_entity:
                continue # no key => no change
            vals = vivo_entity.get(key,[])+source_entity.get(key,[])
            for val in vals:
                if val in vivo_entity and val in source_entity:
                    pass
                elif val in vivo_entity and val not in source_entity:
                    [add, sub] = update_data_property(entity_uri,
                        key_table[key]['predicate'], val, None)
                    ardf = ardf + add
                    srdf = srdf + sub
                else:
                    [add, sub] = update_data_property(entity_uri,
                        key_table[key]['predicate'], None, val)
                    ardf = ardf + add
                    srdf = srdf + sub
        elif action == 'resource_list':
            if key not in source_entity:
                continue # no key => no change
            vals = vivo_entity.get(key,[])+source_entity.get(key,[])
            for val in vals:
                if val in vivo_entity and val in source_entity:
                    pass
                elif val in vivo_entity and val not in source_entity:
                    [add, sub] = update_resource_property(entity_uri,
                        key_table[key]['predicate'], val, None)
                    ardf = ardf + add
                    srdf = srdf + sub
                else:
                    [add, sub] = update_resource_property(entity_uri,
                        key_table[key]['predicate'], None, val)
                    ardf = ardf + add
                    srdf = srdf + sub
        else:
            raise ActionError(action)
    return [ardf, srdf]


def assert_data_property(uri, data_property, value):
    """
    Given a uri, a data_property name, and a value, generate rdf to assert
    the uri has the value of the data property. Value can be a string or a
    dictionary.  If dictionary, sample usage is three elements as shown:

    value = { 'value': val, 'xml:lang': 'en-US',
        'dataype' : 'http://www.w3.org/2001/XMLSchema#string'}

    Note:
    This function does not check that the data property name is valid
    """
    from xml.sax.saxutils import escape
    if isinstance(value, dict):
        val = escape(value['value'])
    else:
        val = escape(value)

    rdf = '    <rdf:Description rdf:about="' + uri + '">'
    rdf = rdf + '\n        <' + data_property
    if isinstance(value, dict) and 'xml:lang' in value:
        rdf = rdf + ' xml:lang="' + value['xml:lang'] + '"'
    if isinstance(value, dict) and 'datatype' in value:
        rdf = rdf + ' datatype="' + value['datatype'] + '"'
    rdf = rdf + '>' + val + '</' + data_property + '>'
    rdf = rdf + '\n    </rdf:Description>\n'
    return rdf


def assert_resource_property(uri, resource_property, resource_uri):
    """
    Given a uri and a resource_property name, and a uri of the resource,
    generate rdf to assert
    assert the uri has the resource_uri for the named resource_property

    Note:
    This function does not check that the resource property name is valid
    This is often called in invertable pairs -- each uri has the other as
    a resource. Example: homeDept and homeDeptFor
    """
    import tempita
    resource_property_template = tempita.Template(
    """    <rdf:Description rdf:about="{{uri}}">
        <{{resource_property}} rdf:resource="{{resource_uri}}"/>
    </rdf:Description>
""")
    rdf = resource_property_template.substitute(uri=uri, \
        resource_property=resource_property, resource_uri=resource_uri)
    return rdf


def update_data_property(uri, data_property, vivo_value, source_value):
    """
    Given the URI of an entity, the name of a data_proprty, the current
    vivo value for the data_property and the source (correct) value for
    the property, use five case logic to generate appropriate subtraction
    and addition rdf to update the data_property. Support values that may
    be dictionaries containing xml:lang and/or dataype assertions

    Note:   we could have shortened the if statements, but they might not have
            been as clear
    """
    srdf = ""
    ardf = ""
    if vivo_value is None and source_value is None:
        pass
    elif vivo_value is None and source_value is not None:
        ardf = assert_data_property(uri, data_property, source_value)
    elif vivo_value is not None and source_value is None:
        srdf = assert_data_property(uri, data_property, vivo_value)
    elif vivo_value is not None and source_value is not None:
        if isinstance(vivo_value,dict) and isinstance(source_value,dict):
            if len(set(vivo_value.keys()) - set(source_value.keys())) != 0:
                equal_values = False
            else:
                equal_values = True
                for key in vivo_value.keys():
                    if vivo_value[key] != source_value[key]:
                        equal_values = False
                        continue
        elif isinstance(vivo_value,dict):
            equal_values = vivo_value['value'] == source_value and\
                'xml:lang' not in vivo_value and 'datatype' not in vivo_value
        elif isinstance(source_value, dict):
            equal_values = vivo_value == source_value['value'] and\
                'xml:lang' not in source_value and 'datatype'\
                not in source_value
        else:
            equal_values = vivo_value == source_value
        if equal_values:
            pass
        else:
            srdf = assert_data_property(uri, data_property, vivo_value)
            ardf = assert_data_property(uri, data_property, source_value)
    return [ardf, srdf]


def update_resource_property(uri, resource_property, vivo_value, source_value):
    """
    Given the URI of an entity, the name of a resource_proprty, the current
    vivo value for the resource_property and the source (correct) value for
    the property, use five case logic to generate appropriate subtraction
    and addtion rdf to update the resource_property

    Note:   we could have shortened the if statements, but they might not have
            been as clear
    """
    srdf = ""
    ardf = ""
    if vivo_value is None and source_value is None:
        pass
    elif vivo_value is None and source_value is not None:
        ardf = assert_resource_property(uri, resource_property, source_value)
    elif vivo_value is not None and source_value is None:
        srdf = assert_resource_property(uri, resource_property, vivo_value)
    elif vivo_value is not None and source_value is not None and \
        vivo_value == source_value:
        pass
    elif vivo_value is not None and source_value is not None and \
        vivo_value != source_value:
        srdf = assert_resource_property(uri, resource_property, vivo_value)
        ardf = assert_resource_property(uri, resource_property, source_value)
    return [ardf, srdf]


def tag_predicate(p):
    """
    Given a full URI predicate, return a tagged predicate.
    So, for example, given

        http://www.w3.org/1999/02/22-rdf-syntax-ns#type

    return

        rdf:type
    """
    ns = {
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#":"rdf:",
        "http://www.w3.org/2000/01/rdf-schema#":"rdfs:",
        "http://www.w3.org/2001/XMLSchema#":"xsd:",
        "http://www.w3.org/2002/07/owl#":"owl:",
        "http://www.w3.org/2003/11/swrl#":"swrl:",
        "http://www.w3.org/2003/11/swrlb#":"swrlb:",
        "http://vitro.mannlib.cornell.edu/ns/vitro/0.7#":"vitro:",
        "http://purl.org/ontology/bibo/":"bibo:",
        "http://purl.org/spar/c4o/":"c4o:",
        "http://purl.org/spar/cito/":"cito:",
        "http://purl.org/dc/terms/":"dcterms:",
        "http://purl.org/NET/c4dm/event.owl#":"event:",
        "http://purl.org/spar/fabio/":"fabio:",
        "http://xmlns.com/foaf/0.1/":"foaf:",
        "http://aims.fao.org/aos/geopolitical.owl#":"geo:",
        "http://purl.obolibrary.org/obo/":"obo:",
        "http://purl.org/net/OCRe/research.owl#":"ocrer:",
        "http://purl.org/net/OCRe/study_design.owl#":"ocresd:",
        "http://www.w3.org/2004/02/skos/core#":"skos:",
        "http://vivo.ufl.edu/ontology/vivo-ufl/":"ufVivo:",
        "http://www.w3.org/2006/vcard/ns#":"vcard:",
        "http://vitro.mannlib.cornell.edu/ns/vitro/public#":"vitro-public:",
        "http://vivoweb.org/ontology/core#":"vivo:",
        "http://vivoweb.org/ontology/scientific-research#":"scires:"
    }
    for uri, tag in ns.items():
        if p.find(uri) > -1:
            newp = p.replace(uri, tag)
            return newp
    return None


def untag_predicate(p):
    """
    Given a tagged predicate, return a full predicate.
    So, for example, given

    rdf:type

    return

        http://www.w3.org/1999/02/22-rdf-syntax-ns#type
    """
    ns = {
        "rdf:":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs:":"http://www.w3.org/2000/01/rdf-schema#",
        "xsd:":"http://www.w3.org/2001/XMLSchema#",
        "owl:":"http://www.w3.org/2002/07/owl#",
        "swrl:":"http://www.w3.org/2003/11/swrl#",
        "swrlb:":"http://www.w3.org/2003/11/swrlb#",
        "vitro:":"http://vitro.mannlib.cornell.edu/ns/vitro/0.7#",
        "bibo:":"http://purl.org/ontology/bibo/",
        "c4o:":"http://purl.org/spar/c4o/",
        "cito:":"http://purl.org/spar/cito/",
        "dcterms:":"http://purl.org/dc/terms/",
        "event:":"http://purl.org/NET/c4dm/event.owl#",
        "fabio:":"http://purl.org/spar/fabio/",
        "foaf:":"http://xmlns.com/foaf/0.1/",
        "geo:":"http://aims.fao.org/aos/geopolitical.owl#",
        "obo:":"http://purl.obolibrary.org/obo/",
        "ocrer:":"http://purl.org/net/OCRe/research.owl#",
        "ocresd:":"http://purl.org/net/OCRe/study_design.owl#",
        "skos:":"http://www.w3.org/2004/02/skos/core#",
        "ufVivo:":"http://vivo.ufl.edu/ontology/vivo-ufl/",
        "vcard:":"http://www.w3.org/2006/vcard/ns#",
        "vitro-public:":"http://vitro.mannlib.cornell.edu/ns/vitro/public#",
        "vivo:":"http://vivoweb.org/ontology/core#",
        "scires:":"http://vivoweb.org/ontology/scientific-research#"
        }
    tag = p[0:p.find(':')+1]
    if tag in ns:
        predicate = p.replace(tag, ns[tag])
        return predicate
    else:
        return None


def merge_uri(from_uri, to_uri):
    """
    Given a from URI and to URI, generate the add and subtract RDF to merge
    all the triples from the from_uri to the to_uri.

    Merge does not allow values of from_uri to be applied to to_uri if the
    predicate is single valued.  This could result in loss of information.
    """

    single_valued_predicates = [
        "rdfs:label",
        "ufVivo:ufid",
        "ufVivo:homeDept",
        "foaf:firstName",
        "foaf:lastName",
        "bibo:namePrefix",
        "bibo:middlename"
        ]
    srdf = ""
    ardf = ""
    if from_uri == to_uri:
        return [ardf, srdf]

    # merge triples

    triples = get_triples(from_uri)["results"]["bindings"]
    for triple in triples:
        sub = ""
        add = ""
        p = tag_predicate(triple["p"]["value"])
        o = triple["o"]
        if o["type"] == "uri":
            sub = assert_resource_property(from_uri, p, o["value"])
            if p not in single_valued_predicates:
                add = assert_resource_property(to_uri, p, o["value"])
        else:
            sub = assert_data_property(from_uri, p, o)
            if p not in single_valued_predicates:
                add = assert_data_property(to_uri, p, o)
        srdf = srdf + sub
        ardf = ardf + add

    # merge references

    triples = get_references(from_uri)["results"]["bindings"]
    for triple in triples:
        s = triple["s"]["value"]
        p = tag_predicate(triple["p"]["value"])
        [add, sub] = update_resource_property(s, p, from_uri, to_uri)
        srdf = srdf + sub
        ardf = ardf + add

    return [ardf, srdf]


def remove_uri(uri):
    """
    Given a URI, generate subtraction URI to remove all triples containing
    the URI as either a subject or object
    """
    srdf = ""

    # Remove triples

    triples = get_triples(uri)["results"]["bindings"]
    for triple in triples:
        p = tag_predicate(triple["p"]["value"])
        o = triple["o"]
        if o["type"] == "uri":
            [add, sub] = update_resource_property(uri, p, o["value"], None)
        else:
            [add, sub] = update_data_property(uri, p, o, None)
        srdf = srdf + sub

    # Remove references

    triples = get_references(uri)["results"]["bindings"]
    for triple in triples:
        s = triple["s"]["value"]
        p = tag_predicate(triple["p"]["value"])
        [add, sub] = update_resource_property(s, p, uri, None)
        srdf = srdf + sub
    return srdf


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

    To Do:
    --  "know" some of the VIVO data elements, checking and converting as
        appropriate.  In particular, handle dates and convert to datetime
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
            i = i + 1
        if heading == []:
            heading = row  # the first row is the heading
            number_of_columns = len(heading)
            continue
        row_number = row_number + 1
        if len(row) == number_of_columns:
            data[row_number] = {}
            i = 0
            for r in row:
                data[row_number][heading[i]] = r
                i = i + 1
        elif skip == False:
            raise RowError("On row "+str(row_number)+", expecting "+
                           str(number_of_columns)+ " data values. Found "+
                           str(len(row))+" data values. Row contents = "+
                           str(row))
        else:
            pass  # row has wrong number of columns and skip is True
    return data


def rdf_header():
    """
    Return a text string containing the standard VIVO RDF prefixes suitable as
    the beginning of an RDF statement to add or remove RDF to VIVO.

    Note:  This function should be updated for each new release of VIVO and to
        include local ontologies and extensions.
    """
    rdf_header = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
    xmlns:rdf     = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs    = "http://www.w3.org/2000/01/rdf-schema#"
    xmlns:xsd     = "http://www.w3.org/2001/XMLSchema#"
    xmlns:owl     = "http://www.w3.org/2002/07/owl#"
    xmlns:swrl    = "http://www.w3.org/2003/11/swrl#"
    xmlns:swrlb   = "http://www.w3.org/2003/11/swrlb#"
    xmlns:vitro   = "http://vitro.mannlib.cornell.edu/ns/vitro/0.7#"
    xmlns:bibo    = "http://purl.org/ontology/bibo/"
    xmlns:c4o     = "http://purl.org/spar/c4o/"
    xmlns:dcelem  = "http://purl.org/dc/elements/1.1/"
    xmlns:dcterms = "http://purl.org/dc/terms/"
    xmlns:event   = "http://purl.org/NET/c4dm/event.owl#"
    xmlns:foaf    = "http://xmlns.com/foaf/0.1/"
    xmlns:fabio   = "http://purl.org/spar/fabio/"
    xmlns:geo     = "http://aims.fao.org/aos/geopolitical.owl#"
    xmlns:pvs     = "http://vivoweb.org/ontology/provenance-support#"
    xmlns:ero     = "http://purl.obolibrary.org/obo/"
    xmlns:scires  = "http://vivoweb.org/ontology/scientific-research#"
    xmlns:skos    = "http://www.w3.org/2004/02/skos/core#"
    xmlns:ufVivo  = "http://vivo.ufl.edu/ontology/vivo-ufl/"
    xmlns:vitro2  = "http://vitro.mannlib.cornell.edu/ns/vitro/public#"
    xmlns:core    = "http://vivoweb.org/ontology/core#"
    xmlns:vivo    = "http://vivoweb.org/ontology/core#">
"""
    return rdf_header


def rdf_footer():
    """
    Return a text string suitable for ending an RDF statement to add or
    remove RDF/XML to/from VIVO
    """
    rdf_footer = """
</rdf:RDF>
"""
    return rdf_footer


def make_rdf_uri(uri):
    """
    Given a uri of a VIVO profile, generate the URI of the corresponding
    RDF page
    """
    k = uri.rfind("/")
    word = uri[k+1:]
    rdf_uri = uri + "/" + word + ".rdf"
    return rdf_uri


def key_string(s):
    """
    Given a string s, return a string with a bunch of punctuation and special
    characters removed and then everything lower cased.  Useful for matching
    strings in which case, punctuation and special characters should not be
    considered in the match
    """
    k = s.encode("utf-8", "ignore").translate(None,
                                              """ \t\n\r\f!@#$%^&*()_+:"<>?-=[]\\;',./""")
    k = k.lower()
    return k


def get_triples(uri):
    """
    Given a VIVO URI, return all the triples referencing that URI as subject
    """
    query = """
    SELECT ?p ?o WHERE
    {
        <{{uri}}> ?p ?o .
    }"""
    query = query.replace("{{uri}}", uri)
    result = vivo_sparql_query(query)
    return result


def get_types(uri):
    """
    Given a VIVO URI, return a list of its types
    """
    types = []
    triples = get_triples(uri)
    if 'results' in triples and 'bindings' in triples['results']:
        rows = triples['results']['bindings']
        for row in rows:
            p = row['p']['value']
            o = row['o']['value']
            if p == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                types.append(o)
    return types


def get_references(uri):
    """
    Given a VIVO uri, return all the triples that have the given uri as an
    object
    """
    query = """
    SELECT ?s ?p WHERE
    {
    ?s ?p <{{uri}}> .
    }"""
    query = query.replace("{{uri}}", uri)
    result = vivo_sparql_query(query)
    return result


def get_vivo_value(uri, predicate):
    """
    Given a VIVO URI, and a predicate, get a value for the predicate.  Assumes
    the result is a single valued string.

    Notes:
    --  if the there are multiple values that meet the criteria, the first one
        is returned
    --  if no values meet the criteria, None is returned
    --  this function is very inefficient, making a SPARQL query for every
        value. Use only when strictly needed!
    """
    query = """
    SELECT ?o
    WHERE
    {
        <{{uri}}> {{predicate}} ?o .
    }
    """
    query = query.replace("{{uri}}", uri)
    query = query.replace("{{predicate}}", predicate)
    result = vivo_sparql_query(query)
    try:
        b = result["results"]["bindings"][0]
        o = b['o']['value']
        return o
    except KeyError:
        return None
    except IndexError:
        return None
    except TypeError:
        return None


def get_value(uri, predicate):
    """
    Given a VIVO URI, and a predicate, get a value for the predicate.  Assumes
    the result is single valued.  The result is a dictionary returned by the
    query.  This enables lang and datatype processing.

    Notes:
    --  if the there are multiple values that meet the criteria, the first one
        is returned
    --  if no values meet the criteria, None is returned
    --  this function is very inefficient, making a SPARQL query for every
        value. Use only when strictly needed!
    """
    query = """
    SELECT ?o WHERE
    {
    <{{uri}}> {{predicate}} ?o .
    }
    """
    query = query.replace("{{uri}}", uri)
    query = query.replace("{{predicate}}", predicate)
    result = vivo_sparql_query(query)
    try:
        b = result["results"]["bindings"][0]
        o = b['o']
        return o
    except KeyError:
        return None


def find_vivo_uri(predicate, value):
    """
    Given a VIVO predicate, and a value, return the first uri in VIVO that
    has that value for the predicate.  Useful for finding URI from values
    of functional properties and key values.

    Notes:
    --  if the there are multiple uris that meet the criteria, the first one
        is returned
    --  if no values meet the criteria, None is returned
    --  this function is very inefficient, making a SPARQL query for every
        value. Use only when strictly needed!
    """
    from vivofoundation import vivo_sparql_query
    query = """
    SELECT ?uri WHERE
    {
    ?uri {{predicate}} "{{value}}" .
    }
    LIMIT 1
    """
    query = query.replace("{{predicate}}", predicate)
    query = query.replace("{{value}}", value)
    result = vivo_sparql_query(query)
    try:
        b = result["results"]["bindings"][0]
        uri = b['uri']['value']
        return uri
    except KeyError:
        return None


def show_triples(triples):
    """
    Given an object returned by get_triples, print the object
    """
    try:
        count = len(triples["results"]["bindings"])
    except KeyError:
        count = 0
    #
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        print "{0:65}".format(p), o
        i = i + 1
    return

def get_organization(organization_uri):
    """
    Given the URI of an organnization, return an object that contains the
    organization it represents.

    As for most of the access functions, additional attributes can be added.
    """
    organization = {'organization_uri':organization_uri}
    organization['uri'] = organization_uri
    organization['sub_organization_within_uris'] = []
    organization['has_sub_organization_uris'] = []
    triples = get_triples(organization_uri)
    try:
        count = len(triples["results"]["bindings"])
    except KeyError:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            organization['label'] = o
        if p == "http://vivoweb.org/ontology/core#subOrganizationWithin":
            organization['sub_organization_within_uris'].append(o)
        if p == "http://vivoweb.org/ontology/core#hasSubOrganization":
            organization['has_sub_organization_uris'].append(o)
        if p == "http://vivoweb.org/ontology/core#overview":
            organization['overview'] = o
        i = i + 1
    return organization


def get_degree(degree_uri):
    """
    Given a URI, return an object that contains the degree (educational
    training) it represents

    """
    degree = {'degree_uri':degree_uri}
    triples = get_triples(degree_uri)
    try:
        count = len(triples["results"]["bindings"])
    except KeyError:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#majorField":
            degree['major_field'] = o

        # deref the academic degree

        if p == "http://vivoweb.org/ontology/core#degreeEarned":
            degree['earned_uri'] = o
            degree['degree_name'] = get_vivo_value(o, 'core:abbreviation')

        # deref the Institution

        if p == "http://vivoweb.org/ontology/core#trainingAtOrganization":
            degree['training_institution_uri'] = o
            institution = get_organization(o)
            if 'label' in institution: # home department might be incomplete
                degree['institution_name'] = institution['label']

        # deref the datetime interval

        if p == "http://vivoweb.org/ontology/core#dateTimeInterval":
            datetime_interval = get_datetime_interval(o)
            degree['datetime_interval'] = datetime_interval
            if 'start_date' in datetime_interval:
                degree['start_date'] = datetime_interval['start_date']
            if 'end_date' in datetime_interval:
                degree['end_date'] = datetime_interval['end_date']
        i = i + 1
    return degree


def get_role(role_uri):
    """
    Given a URI, return an object that contains the role it represents

    To Do:
    Generalize to more types of roles
    """
    role = {'role_uri':role_uri}
    triples = get_triples(role_uri)
    try:
        count = len(triples["results"]["bindings"])
    except KeyError:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#roleIn":
            role['grant_uri'] = o
        if p == "http://vivoweb.org/ontology/core#roleContributesTo":
            role['grant_uri'] = o
        if p == 'http://vivoweb.org/ontology/core#' \
            'co-PrincipalInvestigatorRoleOf':
            role['co_principal_investigator_role_of'] = o
        if p == 'http://vivoweb.org/ontology/core#' \
            'principalInvestigatorRoleOf':
            role['principal_investigator_role_of'] = o
        if p == 'http://vivoweb.org/ontology/core#' \
            'investigatorRoleOf':
            role['investigator_role_of'] = o
        i = i + 1
    return role


def get_webpage(webpage_uri):
    """
    Given a URI, return an object that contains the webpage it represents
    """
    webpage = {'webpage_uri':webpage_uri}
    triples = get_triples(webpage_uri)
    try:
        count = len(triples["results"]["bindings"])
    except KeyError:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#webpageOf":
            webpage['webpage_of'] = o
        if p == "http://vivoweb.org/ontology/core#rank":
            webpage['rank'] = o
        if p == "http://vivoweb.org/ontology/core#linkURI":
            webpage['link_uri'] = o
        if p == "http://vivoweb.org/ontology/core#rank":
            webpage['rank'] = o
        if p == "http://vivoweb.org/ontology/core#linkAnchorText":
            webpage['link_anchor_text'] = o
        if o == "http://vivoweb.org/ontology/ufVivo#FullTextURI":
            webpage['link_type'] = "full_text"
        i = i + 1
    return webpage


def get_datetime_value(datetime_value_uri):
    """
    Given a URI, return an object that contains the datetime value it
    represents
    """
    from datetime import datetime
    datetime_value = {'datetime_value_uri':datetime_value_uri}
    triples = get_triples(datetime_value_uri)
    if 'results' in triples and 'bindings' in triples['results']:
        rows = triples['results']['bindings']
        for row in rows:
            p = row['p']['value']
            o = row['o']['value']
            if p == "http://vivoweb.org/ontology/core#dateTime":
                if len(o) == 10:
                    datetime_value['date_time'] = datetime.strptime(o, "%Y-%m-%d")
                elif len(o) == 19:
                    datetime_value['date_time'] = datetime.strptime(o, "%Y-%m-%dT%H:%M:%S")
                else:
                    print "Length error in datetime", o
            if p == "http://vivoweb.org/ontology/core#dateTimePrecision":
                datetime_value['datetime_precision'] = tag_predicate(o)
    return datetime_value


def get_datetime_interval(datetime_interval_uri):
    """
    Given a URI, return an object that contains the datetime_interval it
    represents
    """
    datetime_interval = {'datetime_interval_uri': datetime_interval_uri}
    triples = get_triples(datetime_interval_uri)
    try:
        count = len(triples["results"]["bindings"])
    except KeyError:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#start":
            datetime_value = get_datetime_value(o)
            datetime_interval['start_date'] = datetime_value
        if p == "http://vivoweb.org/ontology/core#end":
            datetime_value = get_datetime_value(o)
            datetime_interval['end_date'] = datetime_value
        i = i + 1
    return datetime_interval


def make_concept_dictionary(debug=False):
    """
    Make a dictionary for concepts in UF VIVO.  Key is label.  Value is URI.
    """

    global concept_dictionary
    concept_dictionary = {}

    query = """
        SELECT ?uri ?label WHERE
        {
        ?uri a skos:Concept .
        ?uri rdfs:label ?label .
        }"""
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except KeyError:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0], \
            result["results"]["bindings"][1]
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        label = b['label']['value']
        uri = b['uri']['value']
        concept_dictionary[label] = uri
        i = i + 1
    return concept_dictionary


def make_concept_rdf(label):
    """
    Given a concept label, create a concept in VIVO
    """
    concept_template = tempita.Template("""
    <rdf:Description rdf:about="{{concept_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
        <rdfs:label>{{label}}</rdfs:label>
    </rdf:Description>
    """)
    concept_uri = get_vivo_uri()
    rdf = concept_template.substitute(concept_uri=concept_uri, \
        label=label)
    return [rdf, concept_uri]


def make_deptid_dictionary(debug=False):
    """
    Make a dictionary for orgs in UF VIVO.  Key is DeptID.  Value is URI.
    """
    query = """
    SELECT ?x ?deptid WHERE
    {
    ?x rdf:type foaf:Organization .
    ?x ufVivo:deptID ?deptid .
    }"""
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except KeyError:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0], \
            result["results"]["bindings"][1]

    deptid_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        deptid = b['deptid']['value']
        uri = b['x']['value']
        deptid_dictionary[deptid] = uri
        i = i + 1
    return deptid_dictionary


def find_deptid(deptid, deptid_dictionary):
    """
    Given a deptid, find the org with that deptid.  Return True and URI
    if found.  Return false and None if not found
    """
    try:
        uri = deptid_dictionary[deptid]
        found = True
    except KeyError:
        uri = None
        found = False
    return [found, uri]


def make_date_dictionary(datetime_precision="vivo:yearMonthDayPrecision",
                              debug=False):
    """
    Given a VIVO datetime precision, return a dictionary of the URI for each
    date value.
    """
    date_dictionary = {}
    query = tempita.Template("""
    SELECT ?uri ?dt
    WHERE {
      ?uri vivo:dateTimePrecision {{datetime_precision}} .
      ?uri vivo:dateTime ?dt .
    }""")
    query = query.substitute(datetime_precision=datetime_precision)
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except KeyError:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0], \
            result["results"]["bindings"][1]
    #
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        if datetime_precision == "vivo:yearPrecision":
            dt = b['dt']['value'][0:4]
            dtv = datetime.strptime(dt, '%Y')
        elif datetime_precision == "vivo:yearMonthPrecision":
            dt = b['dt']['value'][0:7]
            dtv = datetime.strptime(dt, '%Y-%m')
        elif datetime_precision == "vivo:yearMonthDayPrecision":
            dt = b['dt']['value'][0:10]
            dtv = datetime.strptime(dt, '%Y-%m-%d')
        uri = b['uri']['value']
        date_dictionary[dtv] = uri
        i = i + 1
    return date_dictionary


def make_datetime_interval_dictionary(debug=False):
    """
    Make a dictionary for datetime intervals in UF VIVO.
    Key is concatenation of start and end uris.  Value is URI.
    """
    # TODO write test function
    query = tempita.Template("""
    SELECT ?uri ?starturi ?enduri
    WHERE
    {
        ?uri vivo:end ?enduri .
        ?uri vivo:start ?starturi .
    }
    """)
    query = query.substitute()
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except KeyError:
        count = 0
    if debug:
        print query, count, result["results"]["bindings"][0], \
            result["results"]["bindings"][1]
    #
    datetime_interval_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        uri = b['uri']['value']
        if 'starturi' in b:
            start_uri = b['starturi']['value']
        else:
            start_uri = "None"
        if 'enduri' in b:
            end_uri = b['enduri']['value']
        else:
            end_uri = "None"
        key = start_uri+end_uri
        datetime_interval_dictionary[key] = uri
        i = i + 1
    return datetime_interval_dictionary


def find_datetime_interval(start_uri, end_uri, datetime_dictionary):
    """
    Given start and end uris for dates, find an interval with that pair of
    dates, find the org with that sponsor.  Return True and URI
    Return false and None if not found
    """
    # TODO write test function
    if start_uri == None or start_uri == "":
        start_key = "None"
    else:
        start_key = start_uri

    if end_uri == None or end_uri == "":
        end_key = "None"
    else:
        end_key = end_uri

    try:
        uri = datetime_interval_dictionary[start_key+end_key]
        found = True
    except KeyError:
        uri = None
        found = False
    return [found, uri]


def make_webpage_rdf(full_text_uri, \
    uri_type="http://vivo.ufl.edu/ontology/vivo-ufl/FullTextURL", \
    link_anchor_text="PubMed Central Full Text Link", rank="1", \
    harvested_by="Python PubMed 1.0"):
    """
    Given a uri, create a web page entity with the uri, rank and
    anchor text, harvested_by specified
    """
    if full_text_uri is None:
        return ["", None]
    full_text_url_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{webpage_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#URLLink"/>
        <rdf:type rdf:resource="{{uri_type}}"/>
        <vivo:linkURI>{{full_text_uri}}</vivo:linkURI>
        <vivo:rank>{{rank}}</vivo:rank>
        <vivo:linkAnchorText>{{link_anchor_text}}</vivo:linkAnchorText>
        <ufVivo:harvestedBy>{{harvested_by}}</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    """)
    webpage_uri = get_vivo_uri()
    harvest_datetime = make_harvest_datetime()
    rdf = full_text_url_rdf_template.substitute(webpage_uri=webpage_uri, \
        full_text_uri=full_text_uri, \
        rank=rank, \
        uri_type=uri_type, \
        link_anchor_text=link_anchor_text, \
        harvested_by=harvested_by, \
        harvest_datetime=harvest_datetime)
    return [rdf, webpage_uri]


def get_vivo_uri():
    """
    Find an unused VIVO URI with the specified VIVO_URI_PREFIX
    """
    test_uri = VIVO_URI_PREFIX + 'n' + str(random.randint(1, 9999999999))
    query = """
	SELECT COUNT(?z) WHERE {
	<""" + test_uri + """> ?y ?z
	}"""
    response = vivo_sparql_query(query)
    while int(response["results"]["bindings"][0]['.1']['value']) != 0:
        test_uri = VIVO_URI_PREFIX + str(random.randint(1, 9999999999))
        query = """
            SELECT COUNT(?z) WHERE {
            <""" + test_uri + """> ?y ?z
            }"""
        response = vivo_sparql_query(query)
    return test_uri


def vivo_sparql_query(query,
    baseURL=VIVO_QUERY_URI,
    format="application/sparql-results+json", debug=False):

    """
    Given a SPARQL query string return result set of the SPARQL query.  Default
    is to call the UF VIVO SPAQRL endpoint and receive results in JSON format
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
        "default-graph":"",
        "should-sponge":"soft",
        "query":prefix+query,
        "debug":"on",
        "timeout":"7000",  # 7 seconds
        "format":format,
        "save":"display",
        "fname":""
    }
    querypart = urllib.urlencode(params)
    if debug:
        print "Base URL", baseURL
        print "Query:", querypart
    start = 2.0
    retries = 10
    count = 0
    while True:
        try:
            response = urllib.urlopen(baseURL, querypart).read()
            break
        except KeyError:
            count = count + 1
            if count > retries:
                break
            sleep_seconds = start**count
            print "<!-- Failed query. Count = "+str(count)+\
                " Will sleep now for "+str(sleep_seconds)+\
                " seconds and retry -->"
            time.sleep(sleep_seconds) # increase the wait time with each retry
    try:
        return json.loads(response)
    except KeyError:
        return None