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

from datetime import datetime
from json import dumps
import logging

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2016 Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.8.7"

logger = logging.getLogger(__name__)


class Pump(object):
    """
    The VIVO Pump is a tool for data management using delimited rectangular text files, aka spreadsheets.

    May need a Path class and a Step Class.  For now a Path is a list of Steps.  We will see if that holds up.
    """

    def __init__(self, defn="pump_def.json", src="pump_data.txt"):
        """
        Initialize the pump
        :param defn:  File name of file containing JSON pump definition
        :param src: file name of the csv file to contain VIVO data (get), or csv containing data to update VIVO (update)
        """
        from vivopump import read_update_def, load_enum, DefNotFoundException

        self.update_data = None
        self.original_graph = None
        self.update_graph = None
        self.entity_uri = None  # the entity_uri of the current row being processed in the update_data
        self.out_filename = src
        self.json_def_filename = defn

        #   Simple public instance variables

        self.filter = True
        self.intra = ';'
        self.inter = '\t'
        self.rdfprefix = 'pump'
        self.uriprefix="http://vivo.school.edu/individual/n"

        # Query parms should be properties of the query, not the Pump.  Refactor this

        self.queryuri="http://localhost:8080/vivo/api/sparqlQuery"
        self.username="vivo_root@school.edu"
        self.password="v;bisons"
        self.prefix=('PREFIX rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n'
                     'PREFIX rdfs:     <http://www.w3.org/2000/01/rdf-schema#>\n'
                     'PREFIX xsd:      <http://www.w3.org/2001/XMLSchema#>\n'
                     'PREFIX owl:      <http://www.w3.org/2002/07/owl#>\n'
                     'PREFIX swrl:     <http://www.w3.org/2003/11/swrl#>\n'
                     'PREFIX swrlb:    <http://www.w3.org/2003/11/swrlb#>\n'
                     'PREFIX vitro:    <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>\n'
                     'PREFIX wgs84:    <http://www.w3.org/2003/01/geo/wgs84_pos#>\n'
                     'PREFIX bibo:     <http://purl.org/ontology/bibo/>\n'
                     'PREFIX c4o:      <http://purl.org/spar/c4o/>\n'
                     'PREFIX cito:     <http://purl.org/spar/cito/>\n'
                     'PREFIX event:    <http://purl.org/NET/c4dm/event.owl#>\n'
                     'PREFIX fabio:    <http://purl.org/spar/fabio/>\n'
                     'PREFIX foaf:     <http://xmlns.com/foaf/0.1/>\n'
                     'PREFIX geo:      <http://aims.fao.org/aos/geopolitical.owl#>\n'
                     'PREFIX obo:      <http://purl.obolibrary.org/obo/>\n'
                     'PREFIX ocrer:    <http://purl.org/net/OCRe/research.owl#>\n'
                     'PREFIX ocresd:   <http://purl.org/net/OCRe/study_design.owl#>\n'
                     'PREFIX skos:     <http://www.w3.org/2004/02/skos/core#>\n'
                     'PREFIX uf:       <http://vivo.school.edu/ontology/uf-extension#>\n'
                     'PREFIX vcard:    <http://www.w3.org/2006/vcard/ns#>\n'
                     'PREFIX vitro-public: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>\n'
                     'PREFIX vivo:     <http://vivoweb.org/ontology/core#>\n'
                     'PREFIX scires:   <http://vivoweb.org/ontology/scientific-research#>\n')

        #   Ugly mutable param.  Refactor this

        self.query_parms = {'queryuri': self.queryuri, 'username': self.username, 'password': self.password,
                            'uriprefix': self.uriprefix, 'prefix': self.prefix}

        #   Create the update_def and enumerations

        try:
            self.update_def = read_update_def(defn, self.prefix)
        except IOError:
            raise DefNotFoundException(defn)
        else:
            self.enum = load_enum(self.update_def)  # When the def changes, the enum must be updated

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

    def test(self):
        """
        Produce a string report regarding testing the configuration of the pump
        :return: the string test report
        :rtype: basestring
        """
        from vivopump import new_uri
        from SPARQLWrapper import SPARQLExceptions
        import urllib2

        result = str(datetime.now()) + " Test results" + "\n" + \
            "Update definition\t" + self.json_def_filename + " read.\n" + \
            "Source file name\t" + self.out_filename + ".\n" + \
            "Enumerations read.\n" + \
            "Filters\t" + str(self.filter) + "\n" + \
            "Intra field separator\t" + self.intra + "\n" + \
            "Inter field separator\t" + 'tab\n' if self.inter=='\t' else self.inter + "\n"
        result +=    \
            "VIVO SPARQL API URI\t" + self.query_parms['queryuri'] + "\n" + \
            "VIVO SPARQL API username\t" + self.query_parms['username'] + "\n" + \
            "VIVO SPARQL API password\t" + self.query_parms['password'] + "\n" + \
            "VIVO SPARQL API prefix\t" + self.query_parms['prefix'] + "\n" + \
            "Prefix for RDF file names\t" + self.rdfprefix + "\n" + \
            "Uriprefix for new uri\t" + self.query_parms['uriprefix'] + "\n"

        try:
            uri = new_uri(self.query_parms)
            result += "Sample new uri\t" + uri + "\n" + \
                "Simple VIVO is ready for use.\n"
        except urllib2.HTTPError as herror:
            result += "Connection to VIVO failed\t" + str(herror) + "\n" + \
                "Check your Simple VIVO configuration and your VIVO permissions.\n"
        except SPARQLExceptions.EndPointNotFound as notfound:
            result += "Connection to VIVO failed\t" + str(notfound) + "\n" + \
                "Check your Simple VIVO configuration and your VIVO API.\n"
        except urllib2.URLError as uerror:
            result += "Connection to VIVO failed\t" + str(uerror) + "\n" + \
                "Check your Simple VIVO configuration and your VIVO API.\n"

        result += str(datetime.now()) + " Test end"
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
        import os.path
        import time

        if self.update_data is None:  # Test for injection
            self.update_data = read_csv(self.out_filename, delimiter=self.inter)

        #   Narrow the update_def to include only columns that appear in the update_data

        new_update_columns = {}
        for name, path in self.update_def['column_defs'].items():
            if name in self.update_data[self.update_data.keys()[0]].keys():
                new_update_columns[name] = path
        self.update_def['column_defs'] = new_update_columns

        if self.original_graph is None:  # Test for injection

            # Create the original graph from VIVO

            self.original_graph = get_graph(self.update_def, self.query_parms)

        self.update_graph = Graph()
        for s, p, o in self.original_graph:
            self.update_graph.add((s, p, o))

        logger.info(u'Graphs ready for processing. Original has {} triples.  Update graph has {} triples.'.format(
            len(self.original_graph), len(self.update_graph)))
        logger.info(u'Updates ready for processing. {} rows in update.'.format(len(self.update_data)))

        if len(self.enum) == 0:
            logger.info(u"No enumerations")
        else:
            for key in self.enum.keys():
                logger.info(
                    u"Enumeration {} modified {}. {} entries in get enum.  {} entries in update enum".format(
                        key, time.ctime(os.path.getmtime(key)), len(self.enum[key]['get']),
                        len(self.enum[key]['update'])))
        return self.__do_update()

    def __do_get(self):
        """
        Data is queried from VIVO and returned as a tab delimited text file suitable for
        editing using an editor or spreadsheet, and suitable for use by do_update.

        :return:  Number of rows of data
        """
        from vivopump import vivo_query, make_get_data, unique_path, make_get_query, read_csv, write_csv
        from improve.improve import improve
        import codecs

        #   Generate the get query, execute the query, shape the query results into the return object

        query = make_get_query(self.update_def)
        logger.debug(u"do_get query_parms\n{}".format(self.query_parms))
        logger.debug(u"do_get query\n{}".format(query))
        result_set = vivo_query(query, self.query_parms)
        data = make_get_data(self.update_def, result_set)

        #   Write out the file

        outfile = codecs.open(self.out_filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')

        columns = ['uri'] + self.update_def['entity_def']['order']
        outfile.write(self.inter.join(columns))  # write a header using the inter field separator between column names
        outfile.write('\n')

        for uri in sorted(data.keys()):
            for name in columns:
                if name in data[uri]:

                    #   Translate VIVO values via enumeration if any

                    if name in self.update_def['column_defs']:
                        path = self.update_def['column_defs'][name]

                        #   Warn/correct if path is unique and VIVO is not

                        if unique_path(path) and len(data[uri][name]) > 1:
                            logger.warning(u"VIVO has non-unique values for unique path {} at {} values {}".
                                           format(name, uri, data[uri][name]))
                            data[uri][name] = {next(iter(data[uri][name]))}  # Pick one element from multi-valued set
                            logger.warning(u"Using {}", data[uri][name])

                        #   Handle filters

                        if self.filter and 'filter' in path[len(path) - 1]['object']:
                            a = set()
                            for x in data[uri][name]:
                                was_string = x
                                new_string = improve(path[len(path) - 1]['object']['filter'], x)
                                if was_string != new_string:
                                    logger.debug(u"{} {} {} FILTER IMPROVED {} to {}".
                                                 format(uri, name, path[len(path) - 1]['object']['filter'],
                                                        was_string, new_string))
                                a.add(new_string)
                            data[uri][name] = a

                        #   Handle enumerations

                        if 'enum' in path[len(path) - 1]['object']:
                            enum_name = path[len(path) - 1]['object']['enum']
                            a = set()
                            for x in data[uri][name]:
                                val = self.enum[enum_name]['get'].get(x, '')
                                if val != '':
                                    a.add(val)
                                else:
                                    logger.warning(u"WARNING: Unable to find {} in {}. Blank substituted in {}".
                                                   format(x, enum_name, self.out_filename))
                            data[uri][name] = a

                    #   Gather values into a delimited string

                    val = self.intra.join(data[uri][name])
                    outfile.write(val.replace('\r', ' ').replace('\n', ' ').replace('\t', ' '))
                if name != columns[len(columns) - 1]:
                    outfile.write(self.inter)
            outfile.write('\n')

        outfile.close()

        #   Rewrite the file based on the order_by or uri if none

        sort_column_name = self.update_def['entity_def'].get('order_by', 'uri')
        data = read_csv(self.out_filename, delimiter=self.inter)
        sdata = {}
        try:
            order = sorted(data, key=lambda rown: data[rown][sort_column_name])
        except KeyError:
            logger.error(u"{} in order_by not found.  No such column name. Sorting by uri.".
                         format(sort_column_name))
            order = sorted(data, key=lambda rown: data[rown]['uri'])
        row = 1
        for o in order:
            sdata[row] = data[o]
            row += 1
        write_csv(self.out_filename, sdata, delimiter=self.inter)

        return len(data)

    def __do_merges(self, merges):
        """
        Given merge data collected by processing the action column of the update data, merge all the secondary
        uris to the corresponding primary uris
        :param merges: dictionary of merges.  merge key and two elements.  Primary uri and list of secondary uris
        :return: None
        """

        logger.info(u"Merge Info\n".format(merges))
        for key in merges:
            primary_uri = merges[key]['primary']
            if primary_uri is not None:
                for secondary_uri in merges[key]['secondary']:
                    for s, p, o in self.update_graph.triples((secondary_uri, None, None)):
                        self.update_graph.add((primary_uri, p, o))
                        self.update_graph.remove((secondary_uri, p, o))
                    for s, p, o in self.update_graph.triples((None, None, secondary_uri)):
                        self.update_graph.add((s, p, primary_uri))
                        self.update_graph.remove((s, p, secondary_uri))

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
        logger.debug(u"REMOVING {} triples for {} on row {}".format(removed, uri, row))
        return removed

    def __do_update(self):
        """
        For each row, process each column.  Compare to data in VIVO.  Generate add and sub
        rdf as necessary to process requested add, change, delete
        """
        from rdflib import URIRef, RDF
        from vivopump import new_uri, prepare_column_values, PathLengthException

        merges = {}

        for row, data_update in self.update_data.items():

            # Create a URI if empty

            if data_update['uri'].strip() == '':

                #   If the source uri is empty, create one.  Remaining processing is unchanged.
                #   Since the new uri does not have triples for the columns in the spreadsheet, each will be added

                uri_string = new_uri(self.query_parms)
                logger.debug(u"Adding an entity for row {}. Will be added at {}".format(row, uri_string))
                uri = URIRef(uri_string)
                self.update_graph.add((uri, RDF.type, self.update_def['entity_def']['type']))

            #   Create a URI entity if not found

            else:
                uri = URIRef(data_update['uri'].strip())
                if (uri, None, None) not in self.update_graph:
                    logger.debug(u"Adding an entity for row {}. Will be added at {}".format(row, str(uri)))
                    self.update_graph.add((uri, RDF.type, self.update_def['entity_def']['type']))

            self.entity_uri = uri
            action = data_update.get('action', '').lower()

            #   Process remove action if any

            if action == 'remove':
                self.__do_remove(row, uri)
                continue

            #   Collect merge info if any

            if action != '':
                k = action.find('1')
                if k > -1:
                    key = action[0:k]
                    if key not in merges:
                        merges[key] = {}
                        merges[key]['primary'] = None
                        merges[key]['secondary'] = [uri]
                    else:
                        merges[key]['secondary'].append(uri)
                else:
                    if action not in merges:
                        merges[action] = {}
                    merges[action]['primary'] = uri
                    if 'secondary' not in merges[action]:
                        merges[action]['secondary'] = []

            #   For this row, process all the column_defs and then process closure defs if any.  Closures allow
            #   columns to be "reused" providing additional paths from the row entity to entities in the paths.

            for column_name, column_def in self.update_def['column_defs'].items() + \
                    self.update_def.get('closure_defs', {}).items():

                #   Skip any columns in the data that are not in the update_def

                if column_name not in data_update:
                    continue

                #   Skip the column if it is empty

                if data_update[column_name] == '':
                    logger.debug(u"Skipping blank value. row {} column {}".format(row, column_name))
                    continue

                #   Process the column values, returning a list of RDF elements

                last_def = column_def[len(column_def) - 1]
                column_values = prepare_column_values(data_update[column_name], self.intra, last_def, self.enum, row,
                                                      column_name)

                #   Process the path depending on its length.  Some day we will refactor this to a recursion

                if len(column_def) > 3:
                    raise PathLengthException(
                        "ERROR: Path lengths > 3 not supported.  Path length for " + column_name + " is " + str(
                            len(column_def)))
                elif len(column_def) == 3:
                    self.__do_three_step_update(row, column_name, self.entity_uri, column_def, data_update)
                elif len(column_def) == 2:
                    self.__do_two_step_update(row, column_name, self.entity_uri, column_def, data_update)
                elif len(column_def) == 1:
                    vivo_objs = {unicode(o): o for s, p, o in
                                 self._get_step_triples(self.entity_uri, last_def)}
                    logger.debug(u"{} {} {} {} {}".format(row, column_name, column_values, self.entity_uri, vivo_objs))
                    self.__do_the_update(row, column_name, self.entity_uri, last_def, column_values, vivo_objs)

        if any(merges):
            self.__do_merges(merges)

        #   Return the add and sub graphs representing the changes that need to be made to the original

        add = self.update_graph - self.original_graph  # Triples in update that are not in original
        logger.info(u"Triples to add\n{}".format(add.serialize(format='nt')))
        sub = self.original_graph - self.update_graph  # Triples in original that are not in update
        logger.info(u"Triples to sub\n{}".format(sub.serialize(format='nt')))
        return [add, sub]

    def __do_three_step_update(self, row, column_name, uri, path, data_update):
        """
        Given the current state in the update, and a path length three column_def, add, change or delete intermediate
        and end objects as necessary to perform the requested update
        :param row: row number of the update.  For logger messages
        :param column_name: column_name of the update.  For logger messages
        :param uri: uri of the entity at the head of the path
        :param path: the column definition
        :param data_update: the data provided for the update
        :return: Changes in the update_graph
        """
        from rdflib import RDF, RDFS, Literal, URIRef
        from vivopump import new_uri

        step_def = path[0]
        step_uris = [o for s, p, o in self._get_step_triples(uri, step_def)]

        if len(step_uris) == 0:

            #   VIVO has no values for first intermediate, so add new intermediate and do a two step update on it

            step_uri = URIRef(new_uri(self.query_parms))
            self.update_graph.add((uri, step_def['predicate']['ref'], step_uri))
            self.update_graph.add((step_uri, RDF.type, step_def['object']['type']))
            if 'label' in step_def['object']:
                self.update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'],
                                                                     datatype=step_def['object'].get('datatype', None),
                                                                     lang=step_def['object'].get('lang', None))))
            self.__do_two_step_update(row, column_name, step_uri, path[1:], data_update)

        elif step_def['predicate']['single'] == True:

            #   VIVO has 1 or more values for first intermediate, so we need to see if the predicate
            #   is expected to be single

            step_uri = step_uris[0]
            if len(step_uris) > 1:
                logger.warning(u"WARNING: Single predicate {} has {} values: {}. Using {}".
                               format(path[0]['object']['name'], len(step_uris), step_uris, step_uri))
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
        from vivopump import new_uri, prepare_column_values

        step_def = column_def[0]

        #   Determine the add set (which intermediates point to column values that are not yet in VIVO
        #       For each element in the add set, construct the intermediate and call __do_the_update to
        #       construct the leaf
        #   Determine the sub set (which intermediates point to column values that are in VIVO and are
        #   not in the column values
        #       For each element in the sub set, remove the leaf and the intermediate
        #
        #   This framework should also handle single valued predicates, and cases where there are no step_uris.
        #   That is, it should handle everything.  All the code below should be replaced.

        step_uris = [o for s, p, o in
                     self._get_step_triples(uri, column_def[0])]
        vivo_objs = {}
        for step_uri in step_uris:
            for s, p, o in self._get_step_triples(step_uri, column_def[1]):
                vivo_objs[unicode(o)] = [o, step_uri]

        #   Nasty hack below.  The predicate property "single" appears to have two meanings.  One has to do
        #   with the semantic graph and one has to do with the cardinality of the data column.  These are not
        #   the same.  When the first step is multiple and the second single, the "second single" is not the
        #   cardinality of the data column.  The cardinality of the data column is multiple if any of the
        #   predicates in the path are multiple.  Here we set the cardinality of the leaf to be used by
        #   prepare_column_values and then set it back.  Nasty.  Create a property for leaf cardinality.

        predicate2_cardinality = column_def[1]['predicate']['single']
        if column_def[0]['predicate']['single'] == False:
            column_def[1]['predicate']['single'] = False
        column_values = prepare_column_values(data_update[column_name], self.intra, column_def[1], self.enum, row,
                                              column_name)
        column_def[1]['predicate']['single'] = predicate2_cardinality

        vivo_values = [vivo_objs[x][0] for x in vivo_objs.keys()]
        if unicode(column_values[0]).lower() == 'none':
            add_values = set()
            sub_values = set(vivo_values)
        else:
            add_values = set(column_values) - set(vivo_values)
            sub_values = set(vivo_values) - set(column_values)
            logger.debug(u"Two step SET COMPARE\n\tRow {}\n\tColumn {}\n\tSource values {}\n\tVIVO values {}" +
                         "\n\tAdd values {}\n\tSub values {}\n\tStep_uris {}".
                         format(row, column_name, column_values, vivo_values, add_values, sub_values, step_uris))

        #   Process the adds

        if len(add_values) > 0:
            if column_def[0]['predicate']['single'] == False:

                #   Multiple intermediaries, single valued-leaves

                for leaf_value in add_values:
                    step_uri = URIRef(new_uri(self.query_parms))
                    self.update_graph.add((uri, step_def['predicate']['ref'], step_uri))
                    if 'type' in step_def['object']:
                        self.update_graph.add((step_uri, RDF.type, step_def['object']['type']))
                    if 'label' in step_def['object']:
                        self.update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'],
                                                                             datatype=step_def['object'].get('datatype',
                                                                                                             None),
                                                                             lang=step_def['object'].get('lang',
                                                                                                         None))))
                    self.__do_the_update(row, column_name, step_uri, column_def[1], [leaf_value], {})
            else:

                #   Multiple values on the single leaf

                if len(step_uris) == 0:
                    step_uri = URIRef(new_uri(self.query_parms))
                    self.update_graph.add((uri, step_def['predicate']['ref'], step_uri))
                    if 'type' in step_def['object']:
                        self.update_graph.add((step_uri, RDF.type, step_def['object']['type']))
                    if 'label' in step_def['object']:
                        self.update_graph.add((step_uri, RDFS.label, Literal(step_def['object']['label'],
                                              datatype=step_def['object'].get('datatype', None),
                                              lang=step_def['object'].get('lang', None))))
                else:
                    step_uri = step_uris[0]
                self.__do_the_update(row, column_name, step_uri, column_def[1], column_values, {})

        #   Process the subs

        if len(sub_values) > 0:
            if column_def[0]['predicate']['single'] == False:

                #   Handle multiple intermediaries, single leaves, by removing each intermediary and all its
                #   assertions

                for leaf_value in sub_values:
                    step_uri = vivo_objs[unicode(leaf_value)][1]
                    self.update_graph.remove((uri, step_def['predicate']['ref'], step_uri))
                    self.update_graph.remove((step_uri, None, None))
            else:

                #   Handle single intermediary, possibly multiple leaves, by removing each leaf from the intermediary
                #   Then check to see if the intermediary has any remaining leaf assertions and remove if empty

                step_uri = vivo_objs[unicode(next(iter(sub_values)))][1]
                for leaf_value in sub_values:
                    self.update_graph.remove((step_uri, None, leaf_value))
                g = self.update_graph.triples((step_uri, column_def[1]['predicate']['ref'], None))
                if g == set():
                    self.update_graph.remove((uri, step_def['predicate']['ref'], step_uri))
                    self.update_graph.remove((step_uri, None, None))

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
        from vivopump import make_rdf_term_from_source

        #   Compare VIVO to Input and update as indicated

        if len(column_values) == 1:
            column_string = unicode(column_values[0])
            if column_string == '':
                return None  # No action required if spreadsheet value is empty

            #   boolean processing

            elif step_def['predicate']['single'] == 'boolean':
                if column_string == '1':
                    logger.debug(u"Add boolean value {} to {}".format(step_def['object']['value'], str(uri)))
                    self.update_graph.add((uri, step_def['predicate']['ref'],
                                          make_rdf_term_from_source(step_def['object']['value'], step_def)))
                else:
                    logger.debug(u"Sub boolean value {} from {}".format(step_def['object']['value'], str(uri)))
                    self.update_graph.remove((uri, step_def['predicate']['ref'],
                                             make_rdf_term_from_source(step_def['object']['value'], step_def)))

            #   None processing

            elif column_string == 'None':
                logger.debug(u"Remove {} from {}".format(column_name, str(uri)))
                for vivo_object in vivo_objs.values():
                    self.update_graph.remove((uri, step_def['predicate']['ref'], vivo_object))
                    logger.debug(u"{} {} {}".format(uri, step_def['predicate']['ref'], vivo_object))

            #   Add value processing

            elif len(vivo_objs) == 0:
                logger.debug(u"Adding {} {}".format(column_name, column_string))
                self.update_graph.add((uri, step_def['predicate']['ref'], column_values[0]))  # Literal or URIRef

            #   Update value processing

            else:

                for vivo_object in vivo_objs.values():
                    if vivo_object == column_values[0]:
                        continue  # No action required if vivo term is same as source
                    else:
                        self.update_graph.remove((uri, step_def['predicate']['ref'], vivo_object))
                        logger.debug(u"REMOVE {} {} {}".format(row, column_name, unicode(vivo_object)))
                        self.update_graph.add((uri, step_def['predicate']['ref'], column_values[0]))
                        logger.debug(u"ADD {} {} {} \n\t step_def {} \n\tlang is {}".
                                     format(row, column_name, column_string, step_def, step_def['object'].get('lang',
                                                                                                              None)))
        else:

            #   Set comparison processing

            logger.debug(u'SET COMPARE {} {} {} {}'.format(row, column_name, column_values, vivo_objs.values()))
            add_values = set(column_values) - set(vivo_objs.values())
            sub_values = set(vivo_objs.values()) - set(column_values)
            for value in add_values:
                self.update_graph.add((uri, step_def['predicate']['ref'], value))
            for value in sub_values:
                self.update_graph.remove((uri, step_def['predicate']['ref'], value))

        return None

    def _get_step_triples(self, uri, step_def):
        """
        Return the triples matching the criteria defined in the current step of an update
        :param uri: uri of the entity currently the subject of an update
        :param step_def: step definition from update_def
        :return:  Graph containing zero or more triples that match the criteria for the step
        """
        from rdflib import Graph, RDF
        from vivopump import add_qualifiers, vivo_query, make_rdf_term

        def step_graph(uris, pred, otype=None, graph=self.update_graph):
            """
            Given a list of uri, a pred and a type, return a graph of the update_graph triples satisfying
                uri pred any   <- these are the returned triples
                any a type
            :param uris: list of uris.
            :param pred: the predicate to use in selecting triples for the step_graph
            :param otype: the object type to use.  default in None, and no type selection will be done.
            :param graph: default is update_graph. Closure sieve requires original_graph
            :return: graph
            """
            sg = Graph()
            for suri in uris:
                for obj in graph.objects(suri, pred):
                    if otype is None:
                        sg.add((suri, pred, obj))
                    elif (obj, RDF.type, otype) in self.update_graph:
                        sg.add((suri, pred, obj))

            return sg

        def sieve_triples(sgc, column_name):
            """
            Given a step graph of triples from a closure (sgc), and the current column_name,
            select the triples from the closure graph that have a path from the entity_uri to
            one or more objects in the closure.  If there is no path, return an empty graph.
            :param sgc:  the step closure graph to be "sieved"
            :param column_name: the name of the column to use
            :return: the sieved closure graph
            """

            print "\nBeginning Closure Graph for", column_name
            for (s, p, o) in sgc.triples((None, None, None)):
                print s, p, o

            if len(sgc) == 0:
                return sgc  # Nothing to sieve
            else:
                pred = self.update_def['column_defs'][column_name][0]['predicate']['ref']
                otype = self.update_def['column_defs'][column_name][0]['object'].get('type', None)
                sg = step_graph([self.entity_uri], pred, otype, graph=self.original_graph)
                if len(sg) == 0 or len(self.update_def['column_defs'][column_name]) == 1:
                    return sg
                print "step 0 graph"
                for (s, p, o) in sg.triples((None, None, None)):
                    print s, p, o
                for step in self.update_def['column_defs'][column_name][1:]:
                    sg = step_graph([y for y in sg.objects(None, None)], step['predicate']['ref'],
                                    step['object'].get('type', None), graph=self.original_graph)
                    print "next step graph"
                    for (s, p, o) in sg.triples((None, None, None)):
                        print s, p, o
                if len(sg) == 0:
                    return sg  # column path is empty, so nothing in the closure can match

                #   Wait for it .... Here's the sieve.  Return triples in the closure graph that have
                #   objects on the column graph

                sgr = Graph()
                for (sgcs, sgcp, sgco) in sgc.triples((None, None, None)):
                    if sgco in sg.objects(None, None):
                        sgr.add((sgcs, sgcp, sgco))

                print "reduced step graph"
                for (s, p, o) in sgr.triples((None, None, None)):
                    print s, p, o

            return sgr
        
        if 'qualifier' not in step_def['object']:

            g = step_graph([uri], step_def['predicate']['ref'], step_def['object'].get('type', None))

            # print "\nStep_triples for", step_def['column_name'], [uri],
            # step_def['predicate']['ref'], step_def['object'].get('type', None)

            for (s, p, o) in g.triples((None, None, None)):
                print unicode(s), unicode(p), unicode(o)

            #   If the step_def is in a closure, and its the last step in the closure, then the
            #   closure triples must be sieved against the objects defined by the column.

            if step_def['closure'] and step_def['last']:

                g = sieve_triples(g, step_def['column_name'])
        else:
        
            #   Handle non-specific predicates qualified by SPARQL (a rare case for VIVO-ISF)
            
            q = 'select (?' + step_def['object']['name'] + ' as ?o) where { <' + str(uri) + '> <' + \
                str(step_def['predicate']['ref']) + '> ?' + step_def['object']['name'] + ' . \n' + \
                add_qualifiers([step_def]) + ' }\n'
            logger.debug(u"Qualified Step Triples Query {}".format(q))
            result_set = vivo_query(q, self.query_parms)  # SLOW
            g = Graph()
            for binding in result_set['results']['bindings']:
                o = make_rdf_term(binding['o'])
                g.add((uri, step_def['predicate']['ref'], o))
        logger.debug(u"Step Triples {}".format(g.serialize(format='nt')))
        return g
