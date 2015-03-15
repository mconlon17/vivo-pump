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

# TODO: Continue work on update_def for people, pubs -- medium
# TODO: Control column order via update_def -- difficult
# TODO: Determine and execute a strategy for handling datatypes and language tags in get and update -- medium
# TODO: Add test cases for each data scenario -- medium
# TODO: Add input/output capability to the triple store: stardog and VIVO 1.8 -- difficult

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.56"

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
    The VIVO Pump is a tool for data management using delimited rectangular text files, aka spreadsheets.

    May need a Path class and a Step Class.  For now a Path is a list of Steps.  We will see if that holds up.
    """

    def __init__(self, json_def_filename="data/pump_def.json", out_filename="data/pump_data.txt", verbose=False):
        """
        Initialize the pump
        :param json_def_filename:  File name of file containing JSON pump definition
        """
        from vivopump import read_update_def
        self.update_def = read_update_def(json_def_filename)
        self.update_data = None
        self.original_graph = None
        self.update_graph = None
        self.enum = load_enum(self.update_def)
        self.json_def_filename = json_def_filename
        self.verbose = verbose
        self.out_filename = out_filename

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
            str(datetime.now()) + " Enumerations\n" + dumps(self.enum, indent=4) + "\n" + \
            str(datetime.now()) + " Update Definitions\n" + dumps(self.update_def, indent=4) + "\n" + \
            str(datetime.now()) + " Get Query\n" + make_get_query(self.update_def)
        return result

    def get(self, filename):
        """
        :param filename: Name of the file to write.
        :return: count of the number of rows in the table
        :rtype: int
        """
        self.out_filename = filename
        return do_get(self.update_def, self.enum, self.out_filename, debug=self.verbose)

    def update(self, filename=None):
        """
        Prepare for the update, getting graph and update_data.  Then do the update, producing triples
        """
        from vivopump import read_csv, get_graph
        from rdflib import Graph
        import logging

        logging.basicConfig(level=logging.INFO)
        if filename is not None:
            self.out_filename = filename

        if self.update_data is None:  # Test for injection
            self.update_data = read_csv(self.out_filename, delimiter='\t')

        # Narrow the update_def to include only columns that appears in the update_data

        new_update_columns = {}
        for name, path in self.update_def['column_defs'].items():
            if name in self.update_data['1'].keys():
                new_update_columns[name] = path
        self.update_def['column_defs'] = new_update_columns

        self.enum = load_enum(self.update_def)

        if self.original_graph is None: # Test for injection
            self.original_graph = get_graph(self.update_def, debug=self.verbose)  # Create the original graph from VIVO

        self.update_graph = Graph()
        for s, p, o in self.original_graph:
            self.update_graph.add((s, p, o))

        if self.verbose:
            print datetime.now(), 'Graphs ready for processing. Original has ', len(self.original_graph), \
                '. Update graph has', len(self.update_graph)
            print datetime.now(), 'Updates ready for processing. ', len(self.update_data), 'rows.'
        return self.do_update()

    def do_update(self):
        """
        read updates from a spreadsheet filename.  Compare to data in VIVO.  Generate add and sub
        rdf as necessary to process requested changes
        """
        from rdflib import URIRef, RDF
        from vivopump import new_uri

        # TODO: Support lookup by name or uri -- medium
        # TODO: Support for remove action -- medium

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
                self.update_graph.add((uri, RDF.type, self.update_def['entity_def']['type']))
            entity_uri = uri

            for column_name, column_def in self.update_def['column_defs'].items():
                if column_name not in data_update:
                    continue  # extra column names are allowed in the spreadsheet for annotation
                uri = entity_uri

                if data_update[column_name] == '':
                    continue

                if len(column_def) > 3:
                    raise PathLengthException(
                        "Path lengths > 3 not supported.  Path length for " + column_name + " is " + str(
                            len(column_def)))
                elif len(column_def) == 3:
                    do_three_step_update(row, column_name, uri, column_def, data_update, self.enum, self.update_graph,
                                         debug=False)
                elif len(column_def) == 2:
                    do_two_step_update(row, column_name, uri, column_def, data_update, self.enum, self.update_graph,
                                       debug=False)
                else:
                    step_def = column_def[0]
                    vivo_objs = {}
                    for s, p, o in self.update_graph.triples((uri, step_def['predicate']['ref'], None)):
                        vivo_objs[unicode(o)] = o
                    column_values = prepare_column_values(data_update[column_name], step_def, self.enum, row,
                                                          column_name)
                    if self.verbose:
                        print row, column_name, column_values, uri, vivo_objs
                    do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, self.update_graph,
                                  debug=self.verbose)

        # Return the add and sub graphs representing the changes that need to be made to the original

        add = self.update_graph - self.original_graph  # Triples in update that are not in original
        if self.verbose:
            print "Triples to add"
            print add.serialize(format='nt')
        sub = self.original_graph - self.update_graph  # Triples in original that are not in update
        if self.verbose:
            print "Triples to sub"
            print sub.serialize(format='nt')
        return [add, sub]


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


def do_get(update_def, enum, filename, debug=True):
    """
    Data is queried from VIVO and returned as a tab delimited text file suitable for
    editing using an editor or spreadsheet, and suitable for use by do_update.

    :param filename: Tab delimited file of data from VIVO
    :return:  None.  File is written
    """
    from vivopump import vivo_query
    import codecs

    query = make_get_query(update_def)
    if debug:
        print query
    result_set = vivo_query(query)
    data = make_get_data(update_def, result_set)

    # Write out the file

    outfile = codecs.open(filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')

    columns = (['uri'] + update_def['column_defs'].keys())
    outfile.write('\t'.join(columns))
    outfile.write('\n')

    for uri in sorted(data.keys()):
        for name in columns:
            if name in data[uri]:

                # Translate VIVO values via enumeration if any

                if name in update_def['column_defs']:
                    path = update_def['column_defs'][name]

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
                            a.add(enum[enum_name]['get'].get(x, x))  # if we can't find the value in the
                            # enumeration, just return the value
                        data[uri][name] = a

                # Gather values into a delimited string

                val = ';'.join(data[uri][name])
                outfile.write(val.replace('\r', ' ').replace('\n', ' ').replace('\t', ' '))
            if name != columns[len(columns) - 1]:
                outfile.write('\t')
        outfile.write('\n')

    outfile.close()

    return len(data)


def prepare_column_values(update_string, step_def, enum, row, column_name, debug=False):
    """
    Given the string of data from the update file, the step definition, the row and column name of the
    update_string in the update file, enumerations and filters, prepare the column values and return them
    as a list of strings
    :return: column_values a list of strings
    :rtype: list[str]
    """
    # TODO: How to apply filters to the get processes? -- medium
    # TODO: How/when to apply filters to the update process -- medium
    from vivopump import InvalidDataException, improve_title, repair_email, repair_phone_number, improve_date, \
        improve_dollar_amount, improve_sponsor_award_id, improve_deptid

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
            column_values[i] = enum[step_def['object']['enum']]['update'].get(column_values[i], column_values[i])

    # Handle filters

    if 'filter' in step_def['object']:
        for i in range(len(column_values)):
            was_string = column_values[i]
            if was_string != '' and was_string != 'None':
                column_values[i] = eval(step_def['object']['filter'])(column_values[i])
                if debug and was_string != column_values[i]:
                    print row, column_name, step_def['object'][
                        'filter'], "FILTER IMPROVED", was_string, 'to', \
                        column_values[i]
    return column_values


def do_three_step_update(row, column_name, uri, path, data_update, enum, update_graph, debug=False):
    """
    Given the current state in the update, and a path length three column_def, ad, change or delete intermediate and
    end objects as necessary to perform the requested update
    :param row: row number of the update.  For printing
    :param column_name: column_name of the update.  For printing
    :param uri: uri of the entity at the head of the path
    :param path: the column definition
    :param data_update: the data provided for the update
    :param enum: the enumerations
    :param update_graph: the update graph
    :param debug: debug status.  For printing.
    :return: Changes in the update_graph
    """
    from rdflib import RDF, RDFS, Literal, URIRef
    from vivopump import new_uri

    step_def = path[0]
    step_uris = [o for s, p, o in update_graph.triples((uri, step_def['predicate']['ref'], None))]
    print "Step_uris", step_uris

    if len(step_uris) == 0:

        # VIVO has no values for first intermediate, so add new intermediate and do a two step update on it

        step_uri = URIRef(new_uri())
        update_graph.add((uri, step_def['predicate']['ref'], step_uri))
        update_graph.add((step_uri, RDF.type, step_def['object']['type']))
        if 'label' in step_def['object']:
            update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'])))
        do_two_step_update(row, column_name, step_uri, path[1:], data_update, enum, update_graph, debug=debug)

    elif step_def['predicate']['single']:

        # VIVO has 1 or more values for first intermediate, so we need to see if the predicate is expected to be single

        step_uri = step_uris[0]
        print "found step_uri", step_uri
        if len(step_uris) > 1:
            print "WARNING: Single predicate", path[0]['object']['name'], "has", len(step_uris), "values: ", \
                step_uris, "using", step_uri
        do_two_step_update(row, column_name, step_uri, path[1:], data_update, enum, update_graph, debug=debug)
    return None


def do_two_step_update(row, column_name, uri, column_def, data_update, enum, update_graph, debug=False):
    """
    In a two step update, identify intermediate entity that might need to be created, and end path objects that might
    not yet exist or might need to be created.  Cases are:

                          Predicate Single   Predicate Multiple
    VIVO has 0 values     Add, do_the        Add intermediate, do_the
    VIVO has 1 value         do_the          Set compare through intermediate
    VIVO has >1 value     WARNING, do_the    Set compare through intermediate
    :return: alterations in update graph
    """
    from rdflib import RDF, RDFS, Literal, URIRef
    from vivopump import new_uri
    step_def = column_def[0]

    # Find all the intermediate entities in VIVO and then process cases related to count and defs

    step_uris = [o for s, p, o in update_graph.triples((uri, step_def['predicate']['ref'], None))]

    if len(step_uris) == 0:

        # VIVO has no values for intermediate, so add a new intermediate and do_the_update on the leaf

        step_uri = URIRef(new_uri())
        update_graph.add((uri, step_def['predicate']['ref'], step_uri))
        update_graph.add((step_uri, RDF.type, step_def['object']['type']))
        if 'label' in step_def['object']:
            update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'])))
        uri = step_uri
        step_def = column_def[1]
        vivo_objs = {unicode(o): o for s, p, o in
                     update_graph.triples((uri, step_def['predicate']['ref'], None))}
        column_values = prepare_column_values(data_update[column_name], step_def, enum, row,
                                              column_name)
        do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, update_graph,
                      debug=debug)

    elif step_def['predicate']['single']:

        # VIVO has 1 or more values, so we need to see if the predicate is expected to be single

        step_uri = step_uris[0]
        if len(step_uris) > 1:
            print "WARNING: Single predicate", column_name, "has", len(step_uris), "values: ", \
                step_uris, "using", step_uri
        uri = step_uri
        step_def = column_def[1]
        vivo_objs = {unicode(o): o for s, p, o in
                     update_graph.triples((uri, step_def['predicate']['ref'], None))}
        column_values = prepare_column_values(data_update[column_name], step_def, enum, row,
                                              column_name)
        do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, update_graph,
                      debug=debug)

    else:
        # TODO: Implement set compare through multiple intermediate case -- medium
        print 'WARNING: Updating multi-step predicates not yet implemented'
    return None


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


def load_enum(update_def):
    """
    Find all enumerations in the update_def. for each, read the corresponding enum file and build the corresponding
    pair of enum dictionaries.

    The two columns in the tab delimited input file must be called "short" and "vivo".  "vivo" is the value to put in
    vivo (update) or get from vivo.  short is the human usable short form.

    The input file name must be named enum_name + '.txt', where enum_name appears as the 'enum' value in update_def

    :return enumeration structure.  Pairs of dictionaries, one pair for each enumeration.  short -> vivo, vivo -> short
    """
    # TODO: Provide a path mechanism for enum files.  Current approach assumes in directory with main -- easy
    from vivopump import read_csv
    enum = {}
    for path in update_def['column_defs'].values():
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
