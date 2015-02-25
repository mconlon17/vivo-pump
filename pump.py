#!/usr/bin/env/python

"""
    pump.py: The VIVO Pump

    Read a mapping definition and a spreadsheet and follow the directions to add, update or remove entities and/or
    entity attributes from VIVO.

    Produce a spreadsheet from VIVO that has the entities and attributes ready for editing and updating

    Inputs:  spreadsheet containing updates and additions.  Definition file containing maps to/from columns to
        VIVO objects.  Enumeration tables for translating spreadsheet values to VIVO values and back.  VIVO for
        current state
    Outputs:  spreadsheet with current state.  VIVO state changes. stdout with date times and messages.

    See CHANGELOG.md for history

"""

# TODO: Continue work on UPDATE_DEF for people, pubs -- medium
# TODO: Control column order via update_def -- difficult
# TODO: Determine and execute a strategy for handling datatypes and language tags in get and update -- difficult
# TODO: Add test cases for each data scenario.  There are many -- difficult
# TODO: Add input/output capability to the triple store: stardog and VIVO 1.8 -- difficult

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.48"

UPDATE_DEF = {}
ENUM = {}

from datetime import datetime
from json import dumps


class PathLengthException(Exception):
    """
    Raise this exception when a path definition is longer than the allowable (currently 3)
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class Pump(object):
    """
    The VIVO Pump is a tool for data management using spreadsheets (delimited rectangular text files).

    May need a Path class and a Step Class.  For now a Path is a list of Steps.  We will see if that holds up.
    """

    def __init__(self, json_def_filename="data/pump_def.json", verbose=False):
        """
        Initialize the pump
        :param json_def_filename:  File name of file containing JSON pump definition
        """
        # TODO: Get rid of the global variables UPDATE_DEF and ENUM through proper encapsulation -- medium
        self.update_def = read_update_def(json_def_filename)
        self.column_defs = self.update_def['columns_defs']
        self.update_data = None
        self.original_graph = None
        self.update_graph = None
        global UPDATE_DEF
        UPDATE_DEF = self.update_def
        self.enum = load_enum()
        global ENUM
        ENUM = self.enum
        self.json_def_filename = json_def_filename
        self.verbose = verbose
        self.out_filename = None

    def __str__(self):
        """
        Return a string representation of the pump
        :return: the string representation of the pump
        :rtype: basestring
        """
        return self.serialize()

    def serialize(self):
        """
        Return a string representation of the pump
        :return: the string representation of the pump
        :rtype: basestring
        """
        return dumps(self.update_def)

    def summarize(self):
        """
        Produce a string report summarizing the contents of the pump
        :return: the string summary report
        :rtype: basestring
        """
        result = str(datetime.now()) + " Pump Summary for " + self.json_def_filename + "\n" + \
            str(datetime.now()) + " Enumerations\n" + dumps(ENUM, indent=4) + "\n" + \
            str(datetime.now()) + " Update Definitions\n" + dumps(UPDATE_DEF, indent=4) + "\n" + \
            str(datetime.now()) + " Get Query\n" + make_get_query()
        return result

    def get(self, filename):
        """
        :param filename: Name of the file to write.
        :return: count of the number of rows in the table
        :rtype: int
        """
        self.out_filename = filename
        return do_get(self.out_filename, debug=self.verbose)

    def update(self, filename=None):
        """
        Prepare for the update, getting graph and update_data.  Then do the update, producing triples
        """
        from vivopump import read_csv
        from rdflib import Graph
        self.out_filename = filename
        self.original_graph = get_graph()  # Create the original graph from VIVO using the update_def
        self.update_graph = Graph()
        for s, p, o in self.original_graph:
            self.update_graph.add((s, p, o))
        if self.verbose:
            print datetime.now(), 'Graphs ready for processing. Original has ', len(self.original_graph), \
                '. Update graph has', len(self.update_graph)
        self.update_data = read_csv(self.out_filename, delimiter='\t')
        if self.verbose:
            print datetime.now(), 'Updates ready for processing. ', len(self.update_data), 'rows.'
        return self.do_update()

    def do_update(self):
        """
        read updates from a spreadsheet filename.  Compare to data in VIVO.  generate add and sub
        rdf as necessary to process requested changes
        """
        from rdflib import URIRef, RDF, RDFS, Literal
        from vivopump import new_uri

        # TODO: Support lookup by name or uri -- medium
        # TODO: Support for remove action -- medium
        # TODO: Provide a path mechanism for enum files.  Current approach assumes in directory with main -- easy

        for row, data_update in self.update_data.items():
            uri = URIRef(data_update['uri'])
            if (uri, None, None) not in self.update_graph:

                # If the entity uri can not be found in the update graph, make a new URI ignoring the one in the
                # spreadsheet, if any, and add the URI to the update graph.  Remaining processing is unchanged.
                # Since the new uri does not have triples for the columns in the spreadsheet, each will be added

                uri_string = new_uri()
                if self.verbose:
                    print "Adding an entity for row", row, ".  Will be added at", uri_string
                uri = URIRef(uri_string)
                self.update_graph.add((uri, RDF.type, UPDATE_DEF['entity_def']['type']))
            entity_uri = uri

            for column_name, column_def in self.column_defs.items():
                uri = entity_uri

                if data_update[column_name] == '':
                    continue

                if data_update[column_name] == 'None':

                    # TODO: Replace this approach with one that can handle mini-graph removal when needed -- medium

                    step_def = self.column_defs[len(self.column_defs) - 1]
                    vivo_objs = {unicode(o): o for s, p, o in
                                 self.update_graph.triples((uri, step_def['predicate']['ref'], None))}
                    column_values = prepare_column_values(data_update[column_name], step_def, row, column_name)
                    do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, self.update_graph,
                                  debug=self.verbose)
                    continue

                if len(column_def) > 3:
                    raise PathLengthException(
                        "Path lengths > 3 not supported.  Path length for " + column_name + " is " + str(
                            len(column_def)))

                if len(column_def) == 3:

                    # TODO: Refactor the path logic (including length 3) into a separate function -- difficult

                    # Handle first and second step of length 3 path here.  Likely that additional triples will be needed
                    # in the update graph for finding and processing.  Why do we use a first order graph for update, but
                    # a full graph for get?  Seems inconsistent, under serves update and creates additional code. Also
                    # seems likely that the path 3 logic will need the entire path for examination and processing.  Leaf
                    # actions should remain as they are.

                    continue

                if len(column_def) == 2:

                    # TODO: Test two step path to find intermediate object and use it when singular -- medium

                    step_def = column_def[0]

                    # Find all the intermediate entity uris in VIVO and then process cases related to count and defs

                    step_uris = [o for s, p, o in self.update_graph.triples((uri, step_def['predicate']['ref'], None))]

                    # Here are the cases and actions:
                    #                       Predicate Single   Predicate Multiple
                    # VIVO has 0 values     Add, do_the        Add intermediate, do_the
                    # VIVO has 1 value         do_the          Set compare through intermediate
                    # VIVO has >1 value     WARNING, do_the    Set compare through intermediate

                    if len(step_uris) == 0:

                        # VIVO has no values for intermediate, so add a new intermediate and do_the_update on the leaf

                        step_uri = URIRef(new_uri())
                        self.update_graph.add((uri, step_def['predicate']['ref'], step_uri))
                        self.update_graph.add((step_uri, RDF.type, step_def['object']['type']))
                        if 'label' in step_def['object']:
                            self.update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'])))
                        uri = step_uri
                        step_def = column_def[1]
                        vivo_objs = {unicode(o): o for s, p, o in
                                     self.update_graph.triples((uri, step_def['predicate']['ref'], None))}
                        column_values = prepare_column_values(data_update[column_name], step_def, row, column_name)
                        do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, self.update_graph,
                                      debug=self.verbose)

                    elif step_def['predicate']['single']:

                        # VIVO has 1 or more values, so we need to see if the predicate is expected to be single

                        step_uri = step_uris[0]
                        if len(step_uris) > 1:
                            print "WARNING: Single predicate", column_name, "has", len(step_uris), "values: ", \
                                step_uris, "using", step_uri
                        uri = step_uri
                        step_def = column_def[1]
                        vivo_objs = {unicode(o): o for s, p, o in
                                     self.update_graph.triples((uri, step_def['predicate']['ref'], None))}
                        column_values = prepare_column_values(data_update[column_name], step_def, row, column_name)
                        do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, self.update_graph,
                                      debug=self.verbose)

                    else:
                        # TODO: Implement set compare through multiple intermediate case
                        print 'WARNING: Updating multi-step predicates not yet implemented'
                    continue  # All done with length 2 logic

                # Handle single step predicate

                step_def = column_def[0]

                # Gather all VIVO objects for the column

                vivo_objs = {}
                for s, p, o in self.update_graph.triples((uri, step_def['predicate']['ref'], None)):
                    vivo_objs[unicode(o)] = o

                # Prepare all column values for the column

                column_values = prepare_column_values(data_update[column_name], step_def, row, column_name)
                if self.verbose:
                    print row, column_name, column_values, uri, vivo_objs

                do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, self.update_graph,
                              debug=self.verbose)

        # Write out the triples to be added and subbed in n-triples format

        add = self.update_graph - self.original_graph  # Triples in update that are not in original
        sub = self.original_graph - self.update_graph  # Triples in original that are not in update
        print datetime.now(), "Triples to add:"
        print add.serialize(format='nt')
        print datetime.now(), "Triples to sub:"
        print sub.serialize(format='nt')
        return [len(add), len(sub)]


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
                outfile.write(val.replace('\r', ' ').replace('\n', ' ').replace('\t', ' '))
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
    Given the string of data from the update file, the step definition, the row and column name of the
    update_string in the update file, enumerations and filters, prepare the column values and return them
    as a list of strings
    :return: column_values a list of strings
    :rtype: list[str]
    """
    from vivopump import InvalidDataException, improve_title, repair_email, repair_phone_number

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
            column_values[i] = ENUM[step_def['object']['enum']]['update'].get(column_values[i], column_values[i])

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
    predicates.  Why isn't single valued a special case of multi-valued?  And there will be more questions.

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
            return None  # No action required if spreadsheet value is empty
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
                if unicode(vivo_object) == column_string:
                    continue  # No action required if vivo same as source
                else:
                    update_graph.remove((uri, step_def['predicate']['ref'], vivo_object))
                    if debug:
                        print "REMOVE", row, column_name, unicode(vivo_object)
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
