#!/usr/bin/env/python

"""
    sv_orgs.py: Simple VIVO for Organizations

    Read a spreadsheet and follow the directions to add, update or remove entities and/or
    entity attributes from VIVO.

    Produce a spreadsheet from VIVO that has the entities and attributes ready for editing and updating

    Inputs:  spreadsheet containing updates and additions (stdin).  VIVO for current state
    Outputs:  spreadsheet with current state (stdout).  VIVO state changes

    Log entries indicate errors and actions

    See CHANGELOG.md for history

"""

# TODO: Support for stdin and stdout -- easy
# TODO: Read/write columns defs as JSON.  Then all ingests are just data -- medium
# TODO: Create UPDATE_DEF for people, grants, courses, pubs -- medium
# TODO: Use pyunit for unit level tests -- medium

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.35"

from vivofoundation import read_csv
from datetime import datetime
from rdflib import Namespace, RDF, RDFS
from rdflib.namespace import FOAF
import argparse
import codecs
import json


class PathLengthException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

VIVO = Namespace('http://vivoweb.org/ontology/core#')
VITROP = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/public#')
UFV = Namespace('http://vivo.ufl.edu/ontology/vivo-ufl/')

UPDATE_DEF = {
    'entity_def': {
        'entity_sparql': '?uri a foaf:Organization . ?uri a vivo:ExtensionUnit . ?uri a ufVivo:UFEntity . ',
        'order_by': 'name',
        'type': FOAF.Organization
    },
    'column_defs': {
        'name': [{'predicate': {'ref': RDFS.label, 'single': True}, 'object': {'literal': True}}],
        'type': [{'predicate': {'ref': RDF.type, 'single': False, 'include': ['thing', 'agent', 'org']},
                  'object': {'literal': False, 'enum': 'org_types'}}],
        'within': [{'predicate': {'ref': VIVO.subOrganizationWithin, 'single': False},
                    'object': {'literal': False}}],
        'url': [{'predicate': {'ref': VIVO.webpage, 'single': False},
                 'object': {'literal': False, 'type': VIVO.URLLink, 'name': 'weburi'}},
                {'predicate': {'ref': VIVO.linkURI, 'single': True}, 'object': {'literal': True}}],
        'phone': [{'predicate': {'ref': VIVO.primaryPhone, 'single': True},
                   'object': {'literal': True, 'filter': 'repair_phone_number'}}],
        'email': [{'predicate': {'ref': VIVO.primaryEmail, 'single': True},
                   'object': {'literal': True, 'filter': 'repair_email'}}],
        'address1': [{'predicate': {'ref': VIVO.mailingAddress, 'single': True},
                      'object': {'literal': False, 'type': VIVO.Address, 'name': 'address'}},
                     {'predicate': {'ref': VIVO.address1, 'single': True}, 'object': {'literal': True}}],
        'address2': [{'predicate': {'ref': VIVO.mailingAddress, 'single': True},
                      'object': {'literal': False, 'type': VIVO.Address, 'name': 'address'}},
                     {'predicate': {'ref': VIVO.address2, 'single': True}, 'object': {'literal': True}}],
        'city': [{'predicate': {'ref': VIVO.mailingAddress, 'single': True},
                  'object': {'literal': False, 'type': VIVO.Address, 'name': 'address'}},
                 {'predicate': {'ref': VIVO.addressCity, 'single': True}, 'object': {'literal': True}}],
        'state': [{'predicate': {'ref': VIVO.mailingAddress, 'single': True},
                   'object': {'literal': False, 'type': VIVO.Address, 'name': 'address'}},
                  {'predicate': {'ref': VIVO.addressState, 'single': True}, 'object': {'literal': True}}],
        'zip': [{'predicate': {'ref': VIVO.mailingAddress, 'single': True},
                 'object': {'literal': False, 'type': VIVO.Address, 'name': 'address'}},
                {'predicate': {'ref': VIVO.addressPostalCode, 'single': True}, 'object': {'literal': True}}],
        'photo': [{'predicate': {'ref': VITROP.mainImage, 'single': True},
                   'object': {'literal': False, 'type': VITROP.File, 'name': 'photouri'}},
                  {'predicate': {'ref': VITROP.filename, 'single': True}, 'object': {'literal': True}}],
        'abbreviation': [{'predicate': {'ref': VIVO.abbreviation, 'single': True}, 'object': {'literal': True}}],
        'isni': [{'predicate': {'ref': UFV.isni, 'single': True}, 'object': {'literal': True}}],
        'successor': [{'predicate': {'ref': VIVO.hasSuccessorOrg, 'single': False}, 'object': {'literal': False}}],
        'overview': [{'predicate': {'ref': VIVO.overview, 'single': True}, 'object': {'literal': True}}]
    }
}


def make_get_query():
    """
    Given and update_def, return the sparql query needed to produce a spreadsheet of the data to be managed.
    See do_get
    :return: a sparql query string
    """
    front_query = 'SELECT ?uri ?' + ' ?'.join(UPDATE_DEF['column_defs'].keys()) + '\nWHERE {\n    ' + \
                  UPDATE_DEF['entity_def']['entity_sparql'] + '\n'

    # Fake recursion here to depth 3.  Could be replaced by real recursion to arbitrary path length

    middle_query = ""
    for name, path in UPDATE_DEF['column_defs'].items():
        middle_query += '    OPTIONAL { ?uri <' + str(path[0]['predicate']['ref']) + '> ?'
        if len(path) == 1:
            middle_query += name + ' . }\n'
        else:
            middle_query += path[0]['object']['name'] + ' . \n        OPTIONAL { ?' +\
                path[0]['object']['name'] + ' <' + str(path[1]['predicate']['ref']) + '> ?'
            if len(path) == 2:
                middle_query += name + ' . }}\n'
            else:
                middle_query += path[1]['object']['name'] + ' . \n        OPTIONAL { ?' +\
                    path[1]['object']['name'] + ' <' + str(path[2]['predicate']['ref']) + '> ?'
                if len(path) == 3:
                    middle_query += name + ' . }}}\n'
                else:
                    raise PathLengthException('Path length >3 not supported in do_get')

    back_query = '}\nORDER BY ?' + UPDATE_DEF['entity_def']['order_by']
    return front_query + middle_query + back_query


def do_get(filename):

    """
    Data is queried from VIVO and returned as a tab delimited text file suitable for
    editing using an editor or spreadsheet, and suitable for use by do_update.

    :param filename: Tab delimited file of data from VIVO
    :return:  None.  File is written
    """
    from vivofoundation import vivo_sparql_query

    query = make_get_query()
    print query
    result_set = vivo_sparql_query(query)

    # Create a data structure from the query results that collects the values from
    # the query and has unique uri values.  Multi-valued attributes are collected
    # into lists

    data = {}

    print "Query Results"
    print json.dumps(result_set['results']['bindings'], indent=4)

    for binding in result_set['results']['bindings']:
        uri = str(binding['uri']['value'])
        if uri not in data:
            data[uri] = {}
        for name in ['uri'] + UPDATE_DEF['column_defs'].keys():
            if name in binding:
                if name in data[uri]:
                    data[uri][name].add(binding[name]['value'])
                else:
                    data[uri][name] = set([binding[name]['value']])

    # Write out the file

    outfile = codecs.open(filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')

    columns = (['uri']+UPDATE_DEF['column_defs'].keys())
    outfile.write('\t'.join(columns))
    outfile.write('\n')

    for uri in sorted(data.keys()):
        for name in columns:
            if name in data[uri]:

                # Translate VIVO values via enumeration if any

                if name in UPDATE_DEF['column_defs']:
                    path = UPDATE_DEF['column_defs'][name]
                    if 'enum' in path[len(path)-1]['object']:
                        enum_name = path[len(path)-1]['object']['enum']
                        a = set()
                        for x in data[uri][name]:
                            a.add(enum[enum_name]['get'][x])
                        data[uri][name] = a

                # Gather values into a delimited string

                val = ';'.join(data[uri][name])
                outfile.write(val.replace('\r', ' ').replace('\n', ' '))
            if name != columns[len(columns) - 1]:
                outfile.write('\t')
        outfile.write('\n')

    outfile.close()

    return len(data)


def get_graph():
    """
    Given the update def, get a graph from VIVO of the triples eligible for updating
    :return: graph of triples
    """

    from vivofoundation import vivo_sparql_query
    from rdflib import Graph, URIRef, Literal

    front_query = "SELECT ?uri ?p ?o\nWHERE {\n    "
    back_query = "    ?uri ?p ?o .\n}"
    graph_query = front_query + UPDATE_DEF['entity_def']['entity_sparql'] + back_query
    print 'Graph query\n', graph_query
    triples = vivo_sparql_query(graph_query)
    a = Graph()
    for row in triples['results']['bindings']:
        s = URIRef(row['uri']['value'])
        p = URIRef(row['p']['value'])
        if row['o']['type'] == 'literal' or row['o']['type'] == 'typed-literal':
            o = Literal(row['o']['value'])
            if 'xml:lang' in row:
                o.lang(row['xml:lang'])
            if 'datatype' in row:
                o.datatype(row['o']['datatype'])
        else:
            o = URIRef(row['o']['value'])
        a.add((s, p, o))
    return a


def do_update(filename):
    """
    read updates from a spreadsheet filename.  Compare to data in VIVO.  generate add and sub
    rdf as necessary to process requested changes
    """
    from rdflib import Graph, URIRef, RDFS, RDF, Literal, Namespace
    from rdflib.namespace import FOAF
    from vivofoundation import get_vivo_uri
    from vivopeople import repair_phone_number, repair_email

    # TODO: Additional testing of 2 step path -- medium
    # TODO: Support lookup by name or uri -- medium
    # TODO: Support for remove action -- easy

    column_defs = UPDATE_DEF['column_defs']

    og = get_graph()  # Create the original graph from VIVO using the update_def
    ug = Graph()
    for s, p, o in og:
        ug.add((s, p, o))
    print datetime.now(), 'Graphs ready for processing. Original has ', len(og), '. Update graph has', len(ug)
    data_updates = read_csv(filename, delimiter='\t')
    print datetime.now(), 'Updates ready for processing.  ', filename, 'has ', len(data_updates), 'rows.'
    for row, data_update in data_updates.items():
        uri = URIRef(data_update['uri'])
        if (uri, None, None) not in ug:

            # If the entity uri can not be found in the update graph, make a new URI ignoring the one in the
            # spreadsheet, if any, and add the URI to the update graph.  Remaining processing is unchanged.
            #  Since the new uri does not have triples for the columns in the spreadsheet, each will be added

            uri_string = get_vivo_uri()
            print "Adding an entity for row", row, ".  Will be added at", uri_string
            uri = URIRef(uri_string)
            ug.add((uri, RDF.type, UPDATE_DEF['entity_def']['type']))
        entity_uri = uri

        for column_name, column_def in column_defs.items():
            uri = entity_uri

            if data_update[column_name] == '':
                continue

            #  Perhaps we handle "in order"  step 1, step 2, step last.  The code
            #  we have is for step last.

            if len(column_def) > 3:
                raise PathLengthException(
                    "Path lengths >3 not supported.  Path length for " + column_name + " is " + len(column_def))

            if len(column_def) == 3:

                # Handle first and second step of length 3 path here
                # TODO: Handle length 3 path in do_update -- medium

                pass

            if len(column_def) == 2:
                step_def = column_def[0]
                print "WILL HANDLE", step_def
                step_uri = None
                if step_def['predicate']['single']:

                    # If single valued, try to find it and use last value if VIVO has multiple

                    for s, p, o in ug.triples((uri, step_def['predicate']['ref'], None)):
                        step_uri = o
                if step_uri is None:

                    # If no single value was found, or the predicate is multi-valued, we add another one

                    step_uri = URIRef(get_vivo_uri())
                    ug.add((uri, step_def['predicate']['ref'], step_uri))
                    # TODO: Handle label for intermediate entity -- medium
                uri = step_uri  # the rest of processing of this column refers to the intermediate entity

            # Now handle the last step which is always the same (really?)

            step_def = column_def[len(column_def)-1]

            # Gather all VIVO objects for the column

            vivo_objs = {}
            for s, p, o in ug.triples((uri, step_def['predicate']['ref'], None)):
                vivo_objs[str(o)] = o

            # Gather all column values for the column

            if step_def['predicate']['single']:
                column_values = [data_update[column_name]]
            else:
                column_values = data_update[column_name].split(';')
                if 'include' in step_def['predicate']:
                    column_values += step_def['predicate']['include']

            # Check column values for consistency with single and multi-value attributes

            if step_def['predicate']['single'] and len(column_values) > 1:
                print row, column_name, 'INVALID data.  Predicate is single-valued, multiple values in source.'
                continue
            if '' in column_values and len(column_values) > 1:
                print row, column_name, 'INVALID data.  Blank element in multi-valued predicate set'
                continue
            if 'None' in column_values and len(column_values) > 1:
                print row, column_name, 'INVALID data. None value in multi-valued predicate set'
                continue

            # Handle enumerations

            if 'enum' in step_def['object']:
                for i in range(len(column_values)):
                    column_values[i] = enum[step_def['object']['enum']]['update'].get(column_values[i], None)
                    if column_values[i] is None:
                        print row, column_name, "INVALID", column_values[i], "not found in", \
                            step_def['object']['enum']
                        continue

            # Handle filters

            if 'filter' in step_def['object']:
                for i in range(len(column_values)):
                    was_string = column_values[i]
                    column_values[i] = eval(step_def['object']['filter'])(column_values[i])
                    if was_string != column_values[i]:
                        print row, column_name, step_def['object'][
                            'filter'], "FILTER IMPROVED", was_string, 'to', \
                            column_values[i]

            print row, column_name, column_values, uri, vivo_objs

            # Compare VIVO to Input and update as indicated

            if len(column_values) == 1:
                column_string = column_values[0]
                if column_string == '':
                    continue  # No action required if spreadsheet is blank
                elif column_string == 'None':
                    print "Remove", column_name, "from", str(uri)
                    for vivo_object in vivo_objs.values():
                        ug.remove((uri, step_def['predicate']['ref'], vivo_object))
                        print uri, step_def['predicate']['ref'], vivo_object
                elif len(vivo_objs) == 0:
                    print "Adding", column_name, column_string
                    if step_def['object']['literal']:
                        ug.add((uri, step_def['predicate']['ref'], Literal(column_string)))
                    else:
                        ug.add((uri, step_def['predicate']['ref'], URIRef(column_string)))
                else:
                    for vivo_object in vivo_objs.values():
                        if str(vivo_object) == column_string:
                            continue  # No action required if vivo same as source
                        else:
                            ug.remove((uri, step_def['predicate']['ref'], vivo_object))
                            print "REMOVE", row, column_name, str(vivo_object)
                        if step_def['object']['literal']:
                            ug.add((uri, step_def['predicate']['ref'], Literal(column_string)))
                        else:
                            ug.add((uri, step_def['predicate']['ref'], URIRef(column_string)))
            else:

                # Ready for set comparison

                print 'SET COMPARE', row, column_name, column_values, vivo_objs.keys()

                add_values = set(column_values) - set(vivo_objs.keys())
                sub_values = set(vivo_objs.keys()) - set(column_values)
                for value in add_values:
                    if step_def['object']['literal']:
                        ug.add((uri, step_def['predicate']['ref'], Literal(value)))
                    else:
                        ug.add((uri, step_def['predicate']['ref'], URIRef(value)))
                for value in sub_values:
                    ug.remove((uri, step_def['predicate']['ref'], vivo_objs[value]))

    # Write out the triples to be added and subbed in n-triples format

    add = ug - og  # Triples in update that are not in original
    sub = og - ug  # Triples in original that are not in update
    print datetime.now(), "Triples to add:"
    print add.serialize(format='nt')
    print datetime.now(), "Triples to sub:"
    print sub.serialize(format='nt')
    return [len(add), len(sub)]


def load_enum():
    """
    Find all enumerations in the UPDATE_DEF. for each, read the corresponding enum file and build the corresponding
    pair of enum dictionaries.

    The two columns in the tab delimited input file must be called "short" and "vivo".  "vivo" is the value to put in
    vivo (update) or get from vivo.  short is the human usable short form.

    The input file name must be named enum_name + '.txt', where enum_name appears as the 'enum' value in UPDATE_DEF

    :return enumeration structure.  Pairs of dictionaries, one pair for each enumeration.  short -> vivo, vivo -> short
    """
    enum = {}
    for key, path in UPDATE_DEF['column_defs'].items():
        for step in path:
            if 'object' in step and 'enum' in step['object']:
                enum_name = step['object']['enum']
                if enum_name not in enum:
                    enum[enum_name] = {}
                    enum[enum_name]['get'] = {}
                    enum[enum_name]['update'] = {}
                    enum_data = read_csv(enum_name + '.txt', delimiter='\t')
                    for enum_datum in enum_data.values():
                        enum[enum_name]['get'][enum_datum['vivo']] = enum_datum['short']
                        enum[enum_name]['update'][enum_datum['short']] = enum_datum['vivo']
    return enum

# Driver program starts here

print UPDATE_DEF

enum = load_enum()
print datetime.now(), "Enumerations", json.dumps(enum, indent=4)

parser = argparse.ArgumentParser()
parser.add_argument("action", help="desired action.  get = get data from VIVO.  update = update VIVO "
                                   "data from a spreadsheet", default="get", nargs='?')
parser.add_argument("filename", help="name of spreadsheet containing data to be updated in VIVO",
                    default="sv_data.txt", nargs='?')
args = parser.parse_args()

if args.action == 'get':
    n_rows = do_get(args.filename)
    print datetime.now(), n_rows, "rows in", args.filename
elif args.action == 'update':
    [nadd, nsub] = do_update(args.filename)
    print datetime.now(), nadd, 'triples to add', nsub, 'triples to sub'
else:
    print datetime.now(), "Unknown action.  Try sv_orgs -h for help"

