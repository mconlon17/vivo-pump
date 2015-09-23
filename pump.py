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
__version__ = "0.7.0"

from datetime import datetime
from json import dumps


class Pump(object):
    """
    The VIVO Pump is a tool for data management using delimited rectangular text files, aka spreadsheets.

    May need a Path class and a Step Class.  For now a Path is a list of Steps.  We will see if that holds up.
    """

    def __init__(self, json_def_filename="pump_def.json", out_filename="pump_data.txt", verbose=False,
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

        self.update_def = read_update_def(json_def_filename, query_parms['prefix'])
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
        return self.__do_get()

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

            # Create the original graph from VIVO

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

        return self.__do_update()

    def __do_update(self):
        """
        read updates from a spreadsheet filename.  Compare to data in VIVO.  Generate add and sub
        rdf as necessary to process requested changes
        """
        from rdflib import URIRef, RDF
        from vivopump import new_uri, prepare_column_values, get_step_triples, PathLengthException

        for row, data_update in self.update_data.items():
            uri = URIRef(data_update['uri'])

            if 'remove' in data_update.keys() and data_update['remove'].lower() == 'true':
                self.__do_remove(row, uri)
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
                    self.__do_three_step_update(row, column_name, uri, column_def, data_update)
                elif len(column_def) == 2:
                    self.__do_two_step_update(row, column_name, uri, column_def, data_update)
                elif len(column_def) == 1:
                    step_def = column_def[0]
                    vivo_objs = {unicode(o): o for s, p, o in
                                 get_step_triples(self.update_graph, uri, column_name, step_def, self.query_parms,
                                                  self.verbose)}
                    column_values = prepare_column_values(data_update[column_name], self.intra, step_def, self.enum,
                                                          row, column_name)
                    if self.verbose:
                        print row, column_name, column_values, uri, vivo_objs
                    self.__do_the_update(row, column_name, uri, step_def, column_values, vivo_objs)

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

    def __do_remove(self, row, uri):
        """
        Given the row an uri of a remove instruction, find the uri in the update_graph and remove all triples
        associated with it as either a subject or object
        :param row: the row number in the data for the remove instruction
        :param uri: the uri of the entity to be removed
        :return: int: Number of triples removed.  Must have remove =true and uri found in update_graph
        :rtype: int
        """
        before = len(self.update_graph)
        self.update_graph.remove((uri, None, None))
        self.update_graph.remove((None, None, uri))
        after = len(self.update_graph)
        removed = before - after
        if self.verbose:
            print "REMOVING", removed, "triples for ", uri, "on row", row
        return removed

    def __do_get(self):
        """
        Data is queried from VIVO and returned as a tab delimited text file suitable for
        editing using an editor or spreadsheet, and suitable for use by do_update.

        :return:  Number of rows of data
        """
        from vivopump import vivo_query, make_get_data, unique_path, make_get_query, read_csv, write_csv
        import codecs
        import sys
        from vivopump import improve_title, improve_email, improve_phone_number, improve_date, \
            improve_dollar_amount, improve_sponsor_award_id, improve_deptid, improve_display_name

        # We need a generator that produces the order based on the order value in the entity def, or uri order if not
        # present.  When an order value is present, we always have str(uri) as a last sort order since str(uri) is
        # always unique

        #   Generate the get query, execute the query, shape the query results into the return object

        query = make_get_query(self.update_def)
        if self.verbose:
            print self.query_parms
            print query
        result_set = vivo_query(query, self.query_parms, self.verbose)
        data = make_get_data(self.update_def, result_set)

        #   Write out the file

        outfile = codecs.open(self.out_filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')

        columns = ['uri'] + self.update_def['entity_def']['order']
        outfile.write(self.inter.join(columns))  # write a header using the inter field separator between column names
        outfile.write('\n')

        for uri in sorted(data.keys()):  # replace with generator described above to support row order
            for name in columns:
                if name in data[uri]:

                    # Translate VIVO values via enumeration if any

                    if name in self.update_def['column_defs']:
                        path = self.update_def['column_defs'][name]

                        # Warn/correct if path is unique and VIVO is not

                        if unique_path(path) and len(data[uri][name]) > 1:
                            print "WARNING. VIVO has non-unique values for unique path:", name, "at", uri, \
                                data[uri][name]
                            data[uri][name] = {next(iter(data[uri][name]))}  # Pick one element from multi-valued set
                            print data[uri][name]

                        # Handle filters

                        if self.filter and 'filter' in path[len(path) - 1]['object']:
                            a = set()
                            for x in data[uri][name]:
                                was_string = x
                                new_string = eval(path[len(path) - 1]['object']['filter'])(x)
                                if self.verbose and was_string != new_string:
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
                                a.add(self.enum[enum_name]['get'].get(x, x))  # if we can't find the value in the
                                # enumeration, just return the value
                            data[uri][name] = a

                    # Gather values into a delimited string

                    val = self.intra.join(data[uri][name])
                    outfile.write(val.replace('\r', ' ').replace('\n', ' ').replace('\t', ' '))
                if name != columns[len(columns) - 1]:
                    outfile.write(self.inter)
            outfile.write('\n')

        outfile.close()

        # Rewrite the file based on the order_by or uri if none

        sort_column_name = self.update_def['entity_def'].get('order_by', 'uri')
        data = read_csv(self.out_filename, delimiter=self.inter)
        sdata = {}
        try:
            order = sorted(data, key=lambda rown: data[rown][sort_column_name])
        except KeyError:
            print >>sys.stderr, "ERROR: ", sort_column_name, \
                "in order_by not found.  No such column name. Sorting by uri."
            order = sorted(data, key=lambda rown: data[rown]['uri'])
        row = 1
        for o in order:
            sdata[row] = data[o]
            row += 1
        write_csv(self.out_filename, sdata, delimiter=self.inter)

        return len(data)

    def __do_three_step_update(self, row, column_name, uri, path, data_update):
        """
        Given the current state in the update, and a path length three column_def, add, change or delete intermediate
        and end objects as necessary to perform the requested update
        :param row: row number of the update.  For printing
        :param column_name: column_name of the update.  For printing
        :param uri: uri of the entity at the head of the path
        :param path: the column definition
        :param data_update: the data provided for the update
        :return: Changes in the update_graph
        """
        from rdflib import RDF, RDFS, Literal, URIRef
        from vivopump import new_uri, get_step_triples

        step_def = path[0]
        step_uris = [o for s, p, o in get_step_triples(self.update_graph, uri, column_name, step_def, self.query_parms,
                                                       self.verbose)]

        if len(step_uris) == 0:

            # VIVO has no values for first intermediate, so add new intermediate and do a two step update on it

            step_uri = URIRef(new_uri(self.query_parms))
            self.update_graph.add((uri, step_def['predicate']['ref'], step_uri))
            self.update_graph.add((step_uri, RDF.type, step_def['object']['type']))
            if 'label' in step_def['object']:
                self.update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'],
                                                                     datatype=step_def['object'].get('datatype', None),
                                                                     lang=step_def['object'].get('lang', None))))
            self.__do_two_step_update(row, column_name, step_uri, path[1:], data_update)

        elif step_def['predicate']['single']:

            #   VIVO has 1 or more values for first intermediate, so we need to see if the predicate
            #   is expected to be single

            step_uri = step_uris[0]
            if len(step_uris) > 1:
                print "WARNING: Single predicate", path[0]['object']['name'], "has", len(step_uris), "values: ", \
                    step_uris, "using", step_uri
            self.__do_two_step_update(row, column_name, step_uri, path[1:], data_update)
        return None

    def __do_two_step_update(self, row, column_name, uri, column_def, data_update):
        """
        In a two step update, identify intermediate entity that might need to be created, and end path objects that
        might not yet exist or might need to be created.  Cases are:

                              Predicate Single   Predicate Multiple
        VIVO has 0 values     Add, do_the        Add intermediate, do_the
        VIVO has 1 value         do_the          Set compare through intermediate
        VIVO has >1 value     WARNING, do_the    Set compare through intermediate

        :param: row: current row in spreadsheet
        :param: column_name: name of current column in spreadsheet
        :param: uri: uri in VIVO of the current entity
        :param: column_def: the column def for the current column
        :param: data_update: the column_value
        :return: alterations in update graph
        """
        from rdflib import RDF, RDFS, Literal, URIRef
        from vivopump import new_uri, get_step_triples, prepare_column_values

        step_def = column_def[0]

        # Find all the intermediate entities in VIVO and then process cases related to count and defs

        step_uris = [o for s, p, o in get_step_triples(self.update_graph, uri, column_name, step_def, self.query_parms,
                                                       self.verbose)]

        if len(step_uris) == 0:

            # VIVO has no values for intermediate, so add a new intermediate and __do_the_update on the leaf

            step_uri = URIRef(new_uri(self.query_parms))
            self.update_graph.add((uri, step_def['predicate']['ref'], step_uri))
            self.update_graph.add((step_uri, RDF.type, step_def['object']['type']))
            if 'label' in step_def['object']:
                self.update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'],
                                                                     datatype=step_def['object'].get('datatype', None),
                                                                     lang=step_def['object'].get('lang', None))))
            uri = step_uri
            step_def = column_def[1]
            vivo_objs = {unicode(o): o for s, p, o in
                         get_step_triples(self.update_graph, uri, column_name, step_def, self.query_parms,
                                          self.verbose)}
            column_values = prepare_column_values(data_update[column_name], self.intra, step_def, self.enum, row,
                                                  column_name)
            self.__do_the_update(row, column_name, uri, step_def, column_values, vivo_objs)

        elif step_def['predicate']['single']:

            # VIVO has 1 or more values, so we need to see if the predicate is expected to be single

            step_uri = step_uris[0]
            if len(step_uris) > 1:
                print "WARNING: Single predicate", column_name, "has", len(step_uris), "values: ", \
                    step_uris, "using", step_uri
            uri = step_uri
            step_def = column_def[1]
            vivo_objs = {unicode(o): o for s, p, o in
                         get_step_triples(self.update_graph, uri, column_name, step_def, self.query_parms,
                                          self.verbose)}
            column_values = prepare_column_values(data_update[column_name], self.intra, step_def, self.enum, row,
                                                  column_name)
            self.__do_the_update(row, column_name, uri, step_def, column_values, vivo_objs)

        else:
            print "WARNING: Updating multi-valued multi-step predicates such as ", column_name, " not yet implemented"
        return None

    def __do_the_update(self, row, column_name, uri, step_def, column_values, vivo_objs):
        """
        Given the uri of an entity to be updated, the current step definition, column value(s) as rdflib terms,
        vivo object(s), and the update graph, add or remove triples to the update graph as needed to make the
        appropriate adjustments based on column values and the current state of VIVO.  Whew.

        There is likely controversy and refactoring to come here.  For example, None is not supported for multi-valued
        predicates.  Why isn't single valued a special case of multi-valued?  And there will be more questions.

        The code below represents the guts of the update.  Everything else is getting in position.

        :param uri: uri of the current entity
        :param step_def: current step definition (always a leaf in the flow graph)
        :param column_values: list of column values prepared as rdflib terms
        :param vivo_objs: dict of object Literals keyed by string value of literal
        :return: None
        """

        # Compare VIVO to Input and update as indicated

        if len(column_values) == 1:
            column_string = unicode(column_values[0])
            if column_string == '':
                return None  # No action required if spreadsheet value is empty
            elif column_string == 'None':
                if self.verbose:
                    print "Remove", column_name, "from", str(uri)
                for vivo_object in vivo_objs.values():
                    self.update_graph.remove((uri, step_def['predicate']['ref'], vivo_object))
                    if self.verbose:
                        print uri, step_def['predicate']['ref'], vivo_object
            elif len(vivo_objs) == 0:
                if self.verbose:
                    print "Adding", column_name, column_string
                self.update_graph.add((uri, step_def['predicate']['ref'], column_values[0]))
            else:
                for vivo_object in vivo_objs.values():
                    if vivo_object == column_values[0]:
                        continue  # No action required if vivo term is same as source
                    else:
                        self.update_graph.remove((uri, step_def['predicate']['ref'], vivo_object))
                        if self.verbose:
                            print "REMOVE", row, column_name, unicode(vivo_object)
                            print "VIVO was ", unicode(vivo_object)
                            print "Source is", column_string
                        self.update_graph.add((uri, step_def['predicate']['ref'], column_values[0]))
                        if self.verbose:
                            print "ADD   ", row, column_name, column_string
                            print step_def
                            print "lang is ", step_def['object'].get('lang', None)
        else:
            # Ready for set comparison
            if self.verbose:
                print 'SET COMPARE', row, column_name, column_values, vivo_objs.values()

            add_values = set(column_values) - set(vivo_objs.values())
            sub_values = set(vivo_objs.values()) - set(column_values)
            for value in add_values:
                self.update_graph.add((uri, step_def['predicate']['ref'], value))
            for value in sub_values:
                self.update_graph.remove((uri, step_def['predicate']['ref'], value))

        return None
