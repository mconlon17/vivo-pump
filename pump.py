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

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2015 Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.6.4"

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

    def __init__(self, json_def_filename="data/pump_def.json", out_filename="data/pump_data.txt", verbose=False,
                 nofilters=False, inter='\t', intra=';',
                 query_parms={'queryuri': 'http://localhost:8080/vivo/api/sparqlQuery',
                              'username': 'vivo_root@school.edu',
                              'password': 'v;bisons',
                              'uriprefix': 'http://vivo.school.edu/individual/n',
                              'prefix':
'''
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
'''
                 }):
        """
        Initialize the pump
        :param json_def_filename:  File name of file containing JSON pump definition
        """
        from vivopump import read_update_def, load_enum

        self.update_def = read_update_def(json_def_filename)
        self.update_data = None
        self.original_graph = None
        self.update_graph = None
        self.filter = not nofilters
        self.enum = load_enum(self.update_def)
        self.json_def_filename = json_def_filename
        self.verbose = verbose
        self.intra = intra
        self.inter = inter
        self.out_filename = out_filename
        self.query_parms = query_parms

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
        from vivopump import make_get_query
        result = str(datetime.now()) + " Pump Summary for " + self.json_def_filename + "\n" + \
            str(datetime.now()) + " Enumerations\n" + dumps(self.enum, indent=4) + "\n" + \
            str(datetime.now()) + " Update Definitions\n" + dumps(self.update_def, indent=4) + "\n" + \
            str(datetime.now()) + " Get Query\n" + make_get_query(self.update_def)
        return result

    def get(self):
        """
        Perform the Pump get operation -- using the definition, query VIVO, make a spreadsheet and write it to
        a file.
        :return: count of the number of rows in the table
        :rtype: int
        """
        return do_get(self.update_def, self.enum, self.out_filename, self.query_parms, self.inter, self.intra,
                      self.filter, self.verbose)

    def update(self):
        """
        Prepare for the update, getting graph and update_data.  Then do the update, producing triples
        :return: list(graph, graph): The add and sub graphs for performing the update
        """
        from vivopump import read_csv, get_graph
        from rdflib import Graph
        import logging
        import os.path
        import time

        logging.basicConfig(level=logging.INFO)

        if self.update_data is None:  # Test for injection
            self.update_data = read_csv(self.out_filename, delimiter=self.inter)

        # Narrow the update_def to include only columns that appear in the update_data

        new_update_columns = {}
        for name, path in self.update_def['column_defs'].items():
            if name in self.update_data[1].keys():
                new_update_columns[name] = path
        self.update_def['column_defs'] = new_update_columns

        if self.original_graph is None:  # Test for injection

            #   Create the original graph from VIVO

            self.original_graph = get_graph(self.update_def, self.query_parms, debug=self.verbose)


        self.update_graph = Graph()
        for s, p, o in self.original_graph:
            self.update_graph.add((s, p, o))

        if self.verbose:
            print datetime.now(), 'Graphs ready for processing. Original has ', len(self.original_graph), \
                '. Update graph has', len(self.update_graph)
            print datetime.now(), 'Updates ready for processing. ', len(self.update_data), 'rows.'
            if len(self.enum) == 0:
                print datetime.now(), "No enumerations"
            else:
                for key in self.enum.keys():
                    print datetime.now(), key, "modified", time.ctime(os.path.getmtime(key)), \
                        "get", len(self.enum[key]['get']), "update", \
                        len(self.enum[key]['update'])

        return self.do_update()

    def do_update(self):
        """
        read updates from a spreadsheet filename.  Compare to data in VIVO.  Generate add and sub
        rdf as necessary to process requested changes
        """
        from rdflib import URIRef, RDF
        from vivopump import new_uri, prepare_column_values

        for row, data_update in self.update_data.items():
            uri = URIRef(data_update['uri'])

            if 'remove' in data_update.keys() and data_update['remove'].lower() == 'true':
                do_remove(row, uri, self.update_graph, self.verbose)
                continue

            if (uri, None, None) not in self.update_graph:

                # If the entity uri can not be found in the update graph, make a new URI ignoring the one in the
                # spreadsheet, if any, and add the URI to the update graph.  Remaining processing is unchanged.
                # Since the new uri does not have triples for the columns in the spreadsheet, each will be added

                uri_string = new_uri(self.query_parms)
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
                    do_three_step_update(row, column_name, uri, column_def, data_update, self.intra,
                                         self.enum, self.update_graph, self.query_parms, self.verbose)
                elif len(column_def) == 2:
                    do_two_step_update(row, column_name, uri, column_def, data_update, self.intra,
                                       self.enum, self.update_graph, self.query_parms, self.verbose)
                elif len(column_def) == 1:
                    step_def = column_def[0]
                    vivo_objs = {}
                    for s, p, o in self.update_graph.triples((uri, step_def['predicate']['ref'], None)):
                        vivo_objs[unicode(o)] = o
                    column_values = prepare_column_values(data_update[column_name], self.intra, step_def, self.enum,
                                                          row, column_name)
                    if self.verbose:
                        print row, column_name, column_values, uri, vivo_objs
                    do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, self.update_graph,
                                  self.verbose)

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


def do_remove(row, uri, update_graph, debug):
    """
    Given the row, uri, and value of a remove instruction, find the uri in the update_graph and remove all triples
    associated with it as either a subject or object
    :param row: the row number in the data for the remove instruction
    :param uri: the uri of the entity to be removed
    :param update_graph: the update_graph to be altered
    :param debug: boolean.  If true, diagnostic output is generate for stdout
    :return: int: Number of triples removed.  Must have remove =true and uri found in update_graph
    """
    before = len(update_graph)
    update_graph.remove((uri, None, None))
    update_graph.remove((None, None, uri))
    after = len(update_graph)
    removed = before - after
    if debug:
        print "REMOVING", removed, "triples for ", uri, "on row", row
    return removed


def do_get(update_def, enum, filename, query_parms, inter, intra, do_filter, debug):
    """
    Data is queried from VIVO and returned as a tab delimited text file suitable for
    editing using an editor or spreadsheet, and suitable for use by do_update.

    :param filename: Tab delimited file of data from VIVO
    :param: do_filter: boolean if True do the filters, otherwise do not apply filters
    :return:  Number of rows of data
    """
    from vivopump import vivo_query, make_get_data, unique_path, make_get_query
    import codecs
    from vivopump import improve_title, improve_email, improve_phone_number, improve_date, \
        improve_dollar_amount, improve_sponsor_award_id, improve_deptid, improve_display_name

    # We need a generator that produces the order based on the order value in the entity def, or uri order if not
    # present.  When an order value is present, we always have str(uri) as a last sort order since str(uri) is
    #   always unique

    #   Generate the get query, execute the query, shape the query results into the return object

    query = make_get_query(update_def)
    if debug:
        print query_parms
        print query
    result_set = vivo_query(query, query_parms, debug)
    data = make_get_data(update_def, result_set)

    #   Write out the file

    outfile = codecs.open(filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')

    columns = ['uri'] + update_def['entity_def']['order']
    outfile.write(inter.join(columns))  # write a header using the inter field separator between column names
    outfile.write('\n')

    for uri in sorted(data.keys()):  # replace with generator described above to support row order
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

                    # Handle filters

                    if do_filter and 'filter' in path[len(path) - 1]['object']:
                        a = set()
                        for x in data[uri][name]:
                            was_string = x
                            new_string = eval(path[len(path) - 1]['object']['filter'])(x)
                            if debug and was_string != new_string:
                                print uri, name, path[len(path) - 1]['object'][
                                    'filter'], "FILTER IMPROVED", was_string, 'to', \
                                    new_string
                            a.add(new_string)
                        data[uri][name] = a

                    # Handle enumerations

                    if 'enum' in path[len(path) - 1]['object']:
                        enum_name = path[len(path) - 1]['object']['enum']
                        a = set()
                        for x in data[uri][name]:
                            a.add(enum[enum_name]['get'].get(x, x))  # if we can't find the value in the
                            # enumeration, just return the value
                        data[uri][name] = a

                # Gather values into a delimited string

                val = intra.join(data[uri][name])
                outfile.write(val.replace('\r', ' ').replace('\n', ' ').replace('\t', ' '))
            if name != columns[len(columns) - 1]:
                outfile.write(inter)
        outfile.write('\n')

    outfile.close()

    return len(data)


def do_three_step_update(row, column_name, uri, path, data_update, intra, enum, update_graph,
                         query_parms, debug):
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
    :param debug: debug status. For printing.
    :return: Changes in the update_graph
    """
    from rdflib import RDF, RDFS, Literal, URIRef
    from vivopump import new_uri, get_step_triples

    step_def = path[0]
    step_uris = [o for s, p, o in get_step_triples(update_graph, uri, step_def, query_parms, debug)]

    if len(step_uris) == 0:

        # VIVO has no values for first intermediate, so add new intermediate and do a two step update on it

        step_uri = URIRef(new_uri(query_parms))
        update_graph.add((uri, step_def['predicate']['ref'], step_uri))
        update_graph.add((step_uri, RDF.type, step_def['object']['type']))
        if 'label' in step_def['object']:
            update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'],
                                                            datatype=step_def['object'].get('datatype', None),
                                                            lang=step_def['object'].get('lang', None))))
        do_two_step_update(row, column_name, step_uri, path[1:], data_update, intra, enum, update_graph,
                           query_parms, debug=debug)

    elif step_def['predicate']['single']:

        # VIVO has 1 or more values for first intermediate, so we need to see if the predicate is expected to be single

        step_uri = step_uris[0]
        if len(step_uris) > 1:
            print "WARNING: Single predicate", path[0]['object']['name'], "has", len(step_uris), "values: ", \
                step_uris, "using", step_uri
        do_two_step_update(row, column_name, step_uri, path[1:], data_update, intra, enum, update_graph,
                           query_parms, debug=debug)
    return None


def do_two_step_update(row, column_name, uri, column_def, data_update, intra, enum, update_graph,
                       query_parms, debug):
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
    from vivopump import new_uri, get_step_triples, prepare_column_values

    step_def = column_def[0]

    # Find all the intermediate entities in VIVO and then process cases related to count and defs

    step_uris = [o for s, p, o in get_step_triples(update_graph, uri, step_def, query_parms, debug)]

    if len(step_uris) == 0:

        # VIVO has no values for intermediate, so add a new intermediate and do_the_update on the leaf

        step_uri = URIRef(new_uri(query_parms))
        update_graph.add((uri, step_def['predicate']['ref'], step_uri))
        update_graph.add((step_uri, RDF.type, step_def['object']['type']))
        if 'label' in step_def['object']:
            update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'],
                                                            datatype=step_def['object'].get('datatype', None),
                                                            lang=step_def['object'].get('lang', None))))
        uri = step_uri
        step_def = column_def[1]
        vivo_objs = {unicode(o): o for s, p, o in get_step_triples(update_graph, uri, step_def, query_parms, debug)}
        column_values = prepare_column_values(data_update[column_name], intra, step_def, enum, row,
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
        vivo_objs = {unicode(o): o for s, p, o in get_step_triples(update_graph, uri, step_def, query_parms, debug)}
        column_values = prepare_column_values(data_update[column_name], intra, step_def, enum, row,
                                              column_name)
        do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, update_graph,
                      debug=debug)

    else:
        print "WARNING: Updating multi-valued multi-step predicates such as ", column_name, " not yet implemented"
    return None


def do_the_update(row, column_name, uri, step_def, column_values, vivo_objs, update_graph, debug):
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
                update_graph.add((uri, step_def['predicate']['ref'], Literal(column_string,
                                                                             datatype=step_def['object'].get('datatype',
                                                                                                             None),
                                                                             lang=step_def['object'].get('lang',
                                                                                                         None))))
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
                        print step_def
                        print "lang is ", step_def['object'].get('lang', None)
                    update_graph.add((uri, step_def['predicate']['ref'],
                                      Literal(column_string, datatype=step_def['object'].get('datatype', None),
                                              lang=step_def['object'].get('lang', None))))
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
                update_graph.add((uri, step_def['predicate']['ref'],
                                  Literal(value, datatype=step_def['object'].get('datatype', None),
                                          lang=step_def['object'].get('lang', None))))
            else:
                update_graph.add((uri, step_def['predicate']['ref'], URIRef(value)))
        for value in sub_values:
            update_graph.remove((uri, step_def['predicate']['ref'], vivo_objs[value]))

    return None
