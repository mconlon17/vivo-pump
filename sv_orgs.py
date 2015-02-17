#!/usr/bin/env/python

"""
    sv_orgs.py: The VIVO Pump

    Read a spreadsheet and follow the directions to add, update or remove entities and/or
    entity attributes from VIVO.

    Produce a spreadsheet from VIVO that has the entities and attributes ready for editing and updating

    Inputs:  spreadsheet containing updates and additions.  Enumeration tables for translating
        spreadsheet values to VIVO values and back.  VIVO for current state
    Outputs:  spreadsheet with current state.  VIVO state changes. stdout with date times and messages.

    See CHANGELOG.md for history

"""

# TODO: Continue work on UPDATE_DEF for people, courses, pubs -- medium
# TODO: Control column order via update_def -- difficult
# TODO: Determine and execute a strategy for handling datatypes and language tags -- difficult

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.45"

from datetime import datetime
import argparse


class PathLengthException(Exception):
    """
    Raise this exception when a path definition is longer than the allowable (currently 3)
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


def read_update_def(filename):
    """
    Read an update_def from a file
    :param filename: name of file to read
    :rtype: dict
    :return: JSON object from file
    """

    def fixit(current_object):
        """
        Read the def data structure and replace all string URLs with URIRef entities
        :param current_object: the piece of the data structure to be fixed
        :return current_object: the piece repaired in place
        """
        from rdflib import URIRef
        if isinstance(current_object, dict):
            for k, t in current_object.items():
                if isinstance(t, basestring) and t.startswith('http://'):
                    current_object[k] = URIRef(t)
                else:
                    current_object[k] = fixit(current_object[k])
        elif isinstance(current_object, list):
            for i in range(0, len(current_object)):
                current_object[i] = fixit(current_object[i])
        elif isinstance(current_object, basestring):
            if current_object.startswith("http://"):
                current_object = URIRef(current_object)
        return current_object

    import json
    in_file = open(filename, "r")
    update_def = fixit(json.load(in_file))
    return update_def


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
        middle_query += '    OPTIONAL {  ?uri <' + str(path[0]['predicate']['ref']) + '> ?'
        if len(path) == 1:
            middle_query += name + ' . }\n'
        else:
            middle_query += path[0]['object']['name'] + ' . ?' +\
                path[0]['object']['name'] + ' <' + str(path[1]['predicate']['ref']) + '> ?'
            if len(path) == 2:
                middle_query += name + ' . }\n'
            else:
                middle_query += path[1]['object']['name'] + ' . ?' +\
                    path[1]['object']['name'] + ' <' + str(path[2]['predicate']['ref']) + '> ?'
                if len(path) == 3:
                    middle_query += name + ' . }\n'
                else:
                    raise PathLengthException('Path length >3 not supported in do_get')

    back_query = '}\nORDER BY ?' + UPDATE_DEF['entity_def']['order_by']
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


def make_get_data(result_set):
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
        for name in ['uri'] + UPDATE_DEF['column_defs'].keys():
            if name in binding:
                if name in data[uri]:
                    data[uri][name].add(binding[name]['value'])
                else:
                    data[uri][name] = {binding[name]['value']}
    return data


def do_get(filename, debug=True):

    """
    Data is queried from VIVO and returned as a tab delimited text file suitable for
    editing using an editor or spreadsheet, and suitable for use by do_update.

    :param filename: Tab delimited file of data from VIVO
    :return:  None.  File is written
    """
    from vivopump import vivo_query
    import codecs

    query = make_get_query()
    if debug:
        print query
    result_set = vivo_query(query)
    data = make_get_data(result_set)

    # Write out the file

    outfile = codecs.open(filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')

    columns = (['uri'] + UPDATE_DEF['column_defs'].keys())
    outfile.write('\t'.join(columns))
    outfile.write('\n')

    for uri in sorted(data.keys()):
        for name in columns:
            if name in data[uri]:

                # Translate VIVO values via enumeration if any

                if name in UPDATE_DEF['column_defs']:
                    path = UPDATE_DEF['column_defs'][name]

                    # Warn/correct if path is unique and VIVO is not

                    if unique_path(path) and len(data[uri][name]) > 1:
                        print "WARNING. VIVO has non-unique values for unique path:", name, "at", uri, data[uri][name]
                        data[uri][name] = {next(iter(data[uri][name]))}  # Pick one element from the multi-valued set
                        print data[uri][name]

                    # Handle enumerations

                    if 'enum' in path[len(path) - 1]['object']:
                        enum_name = path[len(path) - 1]['object']['enum']
                        a = set()
                        for x in data[uri][name]:
                            a.add(ENUM[enum_name]['get'].get(x, x))  # if we can't find the value in the enumeration,
                                # just return the value
                        data[uri][name] = a

                # Gather values into a delimited string

                val = ';'.join(data[uri][name])
                outfile.write(val.replace('\r', ' ').replace('\n', ' '))
            if name != columns[len(columns) - 1]:
                outfile.write('\t')
        outfile.write('\n')

    outfile.close()

    return len(data)


def get_graph(debug=False):
    """
    Given the update def, get a graph from VIVO of the triples eligible for updating
    :return: graph of triples
    """

    from vivopump import vivo_query
    from rdflib import Graph, URIRef, Literal

    front_query = "SELECT ?uri ?p ?o\nWHERE {\n    "
    back_query = "    ?uri ?p ?o .\n}"
    graph_query = front_query + UPDATE_DEF['entity_def']['entity_sparql'] + back_query
    if debug:
        print 'Graph query\n', graph_query
    triples = vivo_query(graph_query)
    a = Graph()
    for row in triples['results']['bindings']:
        s = URIRef(row['uri']['value'])
        p = URIRef(row['p']['value'])
        if row['o']['type'] == 'literal' or row['o']['type'] == 'typed-literal':
            o = Literal(row['o']['value'], datatype=row['o'].get('datatype', None),
                        lang=row['o'].get('xml:lang', None))
        else:
            o = URIRef(row['o']['value'])
        a.add((s, p, o))
    return a


def prepare_column_values(update_string, step_def, row, column_name, debug=False):
    """
    Give the string of data from the update file, the step definition, the row and column name of the
    update_string in the update file, enumerations and filters, prepare the column values and return them
    as a list of strings
    :return: column_values a list of strings
    :rtype: list[str]
    """
    from vivopump import InvalidDataException, improve_title

    if step_def['predicate']['single']:
        column_values = [update_string]
    else:
        column_values = update_string.split(';')
        if 'include' in step_def['predicate']:
            column_values += step_def['predicate']['include']

    # Check column values for consistency with single and multi-value attributes

    if step_def['predicate']['single'] and len(column_values) > 1:
        raise InvalidDataException(str(row) + str(column_name) +
                                   'Predicate is single-valued, multiple values in source.')
    if '' in column_values and len(column_values) > 1:
        raise InvalidDataException(str(row) + str(column_name) +
                                   'Blank element in multi-valued predicate set')
    if 'None' in column_values and len(column_values) > 1:
        raise InvalidDataException(str(row) + str(column_name) +
                                   'None value in multi-valued predicate set')

    # Handle enumerations

    if 'enum' in step_def['object']:
        for i in range(len(column_values)):
            column_values[i] = ENUM[step_def['object']['enum']]['update'].get(column_values[i], None)
            if column_values[i] is None:
                raise InvalidDataException(str(row) + str(column_name) + column_values[i] + "not found in" +
                                           step_def['object']['enum'])

    # Handle filters

    if 'filter' in step_def['object']:
        for i in range(len(column_values)):
            was_string = column_values[i]
            column_values[i] = eval(step_def['object']['filter'])(column_values[i])
            if was_string != column_values[i]:
                if debug:
                    print row, column_name, step_def['object'][
                        'filter'], "FILTER IMPROVED", was_string, 'to', \
                        column_values[i]
    return column_values


def do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, update_graph, debug=False):
    """
    Given the uri of an entity to be updated, the current step definition, column value(s), vivo object(s), and
    the update graph, add or remove triples to the update graph as needed to make the appropriate adjustments
    based on column values and the current state of VIVO.  Whew.

    There is likely controversy and refactoring to come here.  For example, None is not supported for multi-valued
    predicates.  Why isn't single valued a special case of multi-valued?  What does the pump do when VIVO has data
    contrary to the flow definition? And there will be more questions.

    The code below represents the guts of the update.  Everything else is getting in position.

    :param uri: uri of the current entity
    :param step_def: current step definition (always a leaf in the flow graph)
    :param column_values: list of prepared column values
    :param vivo_objs: dict of object Literals keyed by string value of literal
    :param update_graph: rdflib graph of the triples in the update set
    :return: None
    """
    from rdflib import Literal, URIRef

    # Compare VIVO to Input and update as indicated

    if len(column_values) == 1:
        column_string = column_values[0]
        if column_string == '':
            return None  # No action required if spreadsheet is blank
        elif column_string == 'None':
            if debug:
                print "Remove", column_name, "from", str(uri)
            for vivo_object in vivo_objs.values():
                update_graph.remove((uri, step_def['predicate']['ref'], vivo_object))
                if debug:
                    print uri, step_def['predicate']['ref'], vivo_object
        elif len(vivo_objs) == 0:
            if debug:
                print "Adding", column_name, column_string
            if step_def['object']['literal']:
                update_graph.add((uri, step_def['predicate']['ref'], Literal(column_string)))
            else:
                update_graph.add((uri, step_def['predicate']['ref'], URIRef(column_string)))
        else:
            for vivo_object in vivo_objs.values():
                if str(vivo_object) == column_string:
                    continue  # No action required if vivo same as source
                else:
                    update_graph.remove((uri, step_def['predicate']['ref'], vivo_object))
                    if debug:
                        print "REMOVE", row, column_name, str(vivo_object)
                if step_def['object']['literal']:
                    if debug:
                        print "ADD   ", row, column_name, column_string
                    update_graph.add((uri, step_def['predicate']['ref'], Literal(column_string)))
                else:
                    update_graph.add((uri, step_def['predicate']['ref'], URIRef(column_string)))
    else:

        # Ready for set comparison
        if debug:
            print 'SET COMPARE', row, column_name, column_values, vivo_objs.keys()

        add_values = set(column_values) - set(vivo_objs.keys())
        sub_values = set(vivo_objs.keys()) - set(column_values)
        for value in add_values:
            if step_def['object']['literal']:
                update_graph.add((uri, step_def['predicate']['ref'], Literal(value)))
            else:
                update_graph.add((uri, step_def['predicate']['ref'], URIRef(value)))
        for value in sub_values:
            update_graph.remove((uri, step_def['predicate']['ref'], vivo_objs[value]))

    return None


def do_update(filename, debug=False):
    """
    read updates from a spreadsheet filename.  Compare to data in VIVO.  generate add and sub
    rdf as necessary to process requested changes
    """
    from rdflib import Graph, URIRef, RDF, RDFS, Literal
    from vivopump import new_uri, read_csv

    # TODO: Support lookup by name or uri -- medium
    # TODO: Support for remove action -- medium

    column_defs = UPDATE_DEF['column_defs']

    original_graph = get_graph()  # Create the original graph from VIVO using the update_def
    update_graph = Graph()
    for s, p, o in original_graph:
        update_graph.add((s, p, o))
    if debug:
        print datetime.now(), 'Graphs ready for processing. Original has ', len(original_graph), '. Update graph has', \
            len(update_graph)
    data_updates = read_csv(filename, delimiter='\t')
    if debug:
        print datetime.now(), 'Updates ready for processing.  ', filename, 'has ', len(data_updates), 'rows.'
    for row, data_update in data_updates.items():
        uri = URIRef(data_update['uri'])
        if (uri, None, None) not in update_graph:

            # If the entity uri can not be found in the update graph, make a new URI ignoring the one in the
            # spreadsheet, if any, and add the URI to the update graph.  Remaining processing is unchanged.
            #  Since the new uri does not have triples for the columns in the spreadsheet, each will be added

            uri_string = new_uri()
            if debug:
                print "Adding an entity for row", row, ".  Will be added at", uri_string
            uri = URIRef(uri_string)
            update_graph.add((uri, RDF.type, UPDATE_DEF['entity_def']['type']))
        entity_uri = uri

        for column_name, column_def in column_defs.items():
            uri = entity_uri

            if data_update[column_name] == '':
                continue

            #  Perhaps we handle "in order"  step 1, step 2, step last.  The update code is step last

            # TODO: Refactor the path logic (including length 3) into a separate function -- difficult

            if len(column_def) > 3:
                raise PathLengthException(
                    "Path lengths > 3 not supported.  Path length for " + column_name + " is " + str(len(column_def)))

            if len(column_def) == 3:

                # Handle first and second step of length 3 path here.  Likely that additional triples will be needed
                # in the update graph for finding and processing.  Why do we use a first order graph for update, but
                # a full graph for get?  Seems inconsistent, under serves update and creates additional code. Also
                # seems likely that the path 3 logic will need the entire path for examination and processing.  Leaf
                # actions should remain as they are.

                pass

            if len(column_def) == 2:
                step_def = column_def[0]
                step_uri = None
                if step_def['predicate']['single']:

                    # If single valued, try to find it and use last value if VIVO has multiple

                    for s, p, o in update_graph.triples((uri, step_def['predicate']['ref'], None)):
                        step_uri = o
                if step_uri is None:

                    # If no single value was found, or the predicate is multi-valued, we add another one

                    step_uri = URIRef(new_uri())
                    update_graph.add((uri, step_def['predicate']['ref'], step_uri))
                    update_graph.add((step_uri, RDF.type, step_def['object']['type']))
                    if 'label' in step_def['object']:
                        update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'])))
                uri = step_uri  # the rest of processing of this column refers to the intermediate entity

            # Now handle the last step which is always the same (really)

            step_def = column_def[len(column_def) - 1]

            # Gather all VIVO objects for the column

            vivo_objs = {}
            for s, p, o in update_graph.triples((uri, step_def['predicate']['ref'], None)):
                vivo_objs[str(o)] = o

            # Prepare all column values for the column

            column_values = prepare_column_values(data_update[column_name], step_def, row, column_name)
            if debug:
                print row, column_name, column_values, uri, vivo_objs

            do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, update_graph, debug=debug)

    # Write out the triples to be added and subbed in n-triples format

    add = update_graph - original_graph  # Triples in update that are not in original
    sub = original_graph - update_graph  # Triples in original that are not in update
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
    from vivopump import read_csv
    enum = {}
    for path in UPDATE_DEF['column_defs'].values():
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

# Driver starts here

from json import dumps

parser = argparse.ArgumentParser()
parser.add_argument("action", help="desired action.  get = get data from VIVO.  update = update VIVO "
                                   "data from a spreadsheet", default="setup", nargs='?')
parser.add_argument("defname", help="name of definition file", default="sv_def.json", nargs="?")

parser.add_argument("filename", help="name of spreadsheet containing data to be updated in VIVO",
                    default="sv_data.txt", nargs='?')
parser.add_argument("--verbose", "-v", action="store_true", help="write verbose processing messages to the log")
args = parser.parse_args()

UPDATE_DEF = read_update_def(args.defname)
ENUM = load_enum()
verbose = args.verbose

print datetime.now(), "Start"
if args.action == 'get':
    n_rows = do_get(args.filename, debug=verbose)
    print datetime.now(), n_rows, "rows in", args.filename
elif args.action == 'update':
    [n_add, n_sub] = do_update(args.filename, debug=verbose)
    print datetime.now(), n_add, 'triples to add', n_sub, 'triples to sub'
elif args.action == 'setup':
    print datetime.now(), "Enumerations\n", dumps(ENUM, indent=4)
    print datetime.now(), "Update Definitions\n", dumps(UPDATE_DEF, indent=4)
    print datetime.now(), "Get Query\n", make_get_query()
else:
    print datetime.now(), "Unknown action.  Try sv_orgs -h for help"
print datetime.now(), "Finish"