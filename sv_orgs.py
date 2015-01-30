#!/usr/bin/env/python

"""
    sv_orgs.py: Simple VIVO for Organizations

    Read a spreadsheet and follow the directions to add, update or remove organizations and/or
    organization attributes from VIVO.

    Produce a spreadsheet from VIVO that has the fields ready for editing and updating

    Inputs:  spreadsheet containing updates and additions (stdin).  VIVO for current state
    Outputs:  spreadsheet with current state (stdout).  VIVO state changes
    Intermediates:  Org triples

    Exceptions are thrown, caught and logged for missing required elements that are missing

    See CHANGELOG.md for history

"""

# TODO: Support for stdin and stdout
# TODO: Read/write columns defs as JSON.  Then all ingests are just data (!)

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.28"

from vivofoundation import read_csv
from datetime import datetime
import argparse
import codecs

# Helper functions start here.  Reusable code for orgs will be moved to vivoorgs


def do_get_orgs(filename):
    from vivofoundation import vivo_sparql_query
    """
    Organization data is queried from VIVO and returned as a tab delimited text file suitable for
    editing using an editor or spreadsheet, and suitable for use by sv_orgs update.
    The following columns are returned:

    uri           VIVO uri of organization
    name          name of organization
    type          type of organization
    url           url of organization web site
    within        uri or name of parent organization(s).  Semi-colon delimited
    overview      text describing organization
    photo         filename of photo
    abbreviation  Abbreviated name of organization
    successor     uri or name of successor if any
    address       semi-colon delimited address lines
    phone         primary phone number
    email         primary email address
    isni          ISNI of org if any

    :param filename: Tab delimited file of org data
    :return:  None.  File is written
    """

    # TODO: Produce the query from the column_defs data structure (!)

    query = """
    SELECT ?uri ?name ?type ?url ?within ?overview ?photo ?abbreviation ?successor ?address1 ?address2 ?city ?state
        ?zip ?phone ?email ?isni
    WHERE {

        ?uri a foaf:Organization .
        ?uri a ufVivo:UFEntity .
        ?uri a vivo:ExtensionUnit .
        ?uri rdf:type ?type .
        FILTER (?type != foaf:Organization && ?type != foaf:Agent && ?type != owl:Thing && ?type != ufVivo:UFEntity)
        ?uri rdfs:label ?name .
        OPTIONAL { ?uri vivo:webpage ?weburi .  ?weburi vivo:linkURI ?url .}
        OPTIONAL { ?uri vivo:subOrganizationWithin ?within . }
        OPTIONAL { ?uri vivo:overview ?overview . }
        OPTIONAL { ?uri vitro-public:mainImage ?photouri . ?photouri vitro-public:filename ?photo .}
        OPTIONAL { ?uri vivo:abbreviation ?abbreviation . }
        OPTIONAL { ?uri vivo:hasSuccessorOrganization ?successor . }
        OPTIONAL { ?uri vivo:mailingAddress ?address .
            OPTIONAL{ ?address vivo:address1 ?address1 . }
            OPTIONAL{ ?address vivo:address2 ?address2 . }
            OPTIONAL{ ?address vivo:addressCity ?city . }
            OPTIONAL{ ?address vivo:addressPostalCode ?zip . }
            OPTIONAL{ ?address vivo:addressState ?state . }
            }
       OPTIONAL { ?uri vivo:phoneNumber ?phone . }
       OPTIONAL { ?uri vivo:email ?email . }
       OPTIONAL { ?uri ufVivo:isni ?isni . }

    }
    ORDER BY ?name
    """

    org_result_set = vivo_sparql_query(query)
    
    orgs = {}
    
    for binding in org_result_set['results']['bindings']:

        uri = binding['uri']['value']
        if uri not in orgs:
            orgs[uri] = {}
    
        #  Each property is either single-valued, multi-valued, and/or de-referenced.  We're not
        #  not ready for de-referenced yet.  That will require more complex SPARQL

        #  Single valued attributes.  If data has more than one value, use the last value found
    
        for name in ('uri', 'name', 'url', 'overview', 'photo', 'abbreviation', 'address1', 'address2', 'city', 'state',
                     'zip', 'phone', 'email', 'isni'):
            if name in binding:
                orgs[uri][name] = binding[name]

        # multi-valued attributes.  Collect all values into lists
        
        for name in ('successor', 'within', 'type'):
            if name in binding:
                if name in orgs[uri]:
                    orgs[uri][name].append(binding[name])
                else:
                    orgs[uri][name] = [binding[name]]

    # Write out the file

    outfile = codecs.open(filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')

    columns = ('uri', 'name', 'type', 'within', 'url', 'phone', 'email', 'address1', 'address2', 'city', 'state',
               'zip', 'photo',
               'abbreviation', 'isni', 'successor', 'overview')
    outfile.write('\t'.join(columns))
    outfile.write('\n')

    for uri in sorted(orgs.keys()):
        for name in columns:
            if name in orgs[uri]:
                if type(orgs[uri][name]) is list:
                    if name == 'type':
                        val = ';'.join(set(org_types.get(x['value'], ' ') for x in orgs[uri][name]))
                    else:
                        val = ';'.join(set(x['value'] for x in orgs[uri][name]))
                else:
                    val = orgs[uri][name]['value'].replace('\n', ' ').replace('\r', ' ')
                outfile.write(val)
            if name != columns[len(columns)-1]:
                outfile.write('\t')
        outfile.write('\n')

    outfile.close()
    
    return len(orgs)


def get_org_triples():
    org_query = """
   SELECT ?s ?p ?o
    WHERE {
        ?s a foaf:Organization .
        ?s a vivo:ExtensionUnit .
        ?s ?p ?o .
    }
    """
    from vivofoundation import vivo_sparql_query
    triples = vivo_sparql_query(org_query)
    print datetime.now(), len(triples["results"]["bindings"]), "org triples"
    return triples


def iri_string(d):
    """
    Given a dict representing the value of an element returned by a fuseki query, generate
    the string version suitable for inclusion in an NT file.
    """
    return '<' + d['value'] + '>'


def iri_predicate(d):
    """
    Give a dict representing the value of an element returned by a fuseki query corresponding
    to the predicate of a triple, return the string version suitable for inclusion in an NT file.
    :param d: dictionary of a value returned by fuseki
    :return: string

    See http://www.w3.org/TR/n-triples/ for standards for n-triples
    """
    if d['type'] == 'literal' or d['type'] == 'typed-literal':
        s = '"' + d['value'].replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r') + '"'
        if 'xml:lang' in d:
            s = s + '@' + d['xml:lang']
        if 'datatype' in d:
            s = s + '^^<' + d['datatype'] + '>'
        return s
    else:
        return iri_string(d)

def write_triples(triples, filename):
    """
    Given a structure from fuseki with the triples, write the triples to a file in nt format

    :param triples: structure from fuseki query with s, p, o
    :param filename: filename to write triples to
    :return:
    """
    import codecs
    outfile = codecs.open('__'+filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')
    for row in triples['results']['bindings']:
        outfile.write(iri_string(row['s']))
        outfile.write(' ')
        outfile.write(iri_string(row['p']))
        outfile.write(' ')
        outfile.write(iri_predicate(row['o']))
        outfile.write(' .\n')
    outfile.close()
    return


def do_update_orgs(filename):
    """
    read updates from a spreadsheet filename.  Compare to orgs in VIVO.  generate add and sub
    rdf as necessary to process requested changes
    """
    from rdflib import Graph, URIRef, RDFS, RDF, Literal, Namespace
    from rdflib.namespace import FOAF
    from vivofoundation import get_vivo_uri
    from vivopeople import repair_phone_number, repair_email

    # TODO: Handle multiple values -- medium
    # TODO: Handle intermediate entity -- difficult
    # TODO: Support lookup by name or uri -- medium
    # TODO: Support for remove action -- easy
    # TODO: Handle highest level entity subject (!) -- medium

    VIVO = Namespace('http://vivoweb.org/ontology/core#')
    VITROP = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/public#')
    UFV = Namespace('http://vivo.ufl.edu/ontology/vivo-ufl/')

    column_defs = {
        'name': [{'predicate': RDFS.label, 'object': {'literal': True}}],
        'type': [{'predicate': RDF.type, 'object': {'literal': False, 'enum': 'org_uris'}}],
        'within': [{'predicate': VIVO.subOrganizationWithin, 'object': {'literal': False}}],
        'url': [{'predicate': VIVO.webPage, 'object': {'literal': True}},
                {'predicate': VIVO.linkURI, 'object': {'literal': True}}],
        'phone': [{'predicate': VIVO.primaryPhone, 'object': {'literal': True, 'filter': 'repair_phone_number'}}],
        'email': [{'predicate': VIVO.primaryEmail, 'object': {'literal': True, 'filter': 'repair_email'}}],
        'address1': [{'predicate': VIVO.mailingAddress, 'object': {'literal': False}},
                     {'predicate': VIVO.address1, 'object': {'literal': True}}],
        'address2': [{'predicate': VIVO.mailingAddress, 'object': {'literal': False}},
                     {'predicate': VIVO.address2, 'object': {'literal': True}}],
        'city': [{'predicate': VIVO.mailingAddress, 'object': {'literal': False}},
                 {'predicate': VIVO.addressCity, 'object': {'literal': True}}],
        'state': [{'predicate': VIVO.mailingAddress, 'object': {'literal': False}},
                  {'predicate': VIVO.addressState, 'object': {'literal': True}}],
        'zip': [{'predicate': VIVO.mailingAddress, 'object': {'literal': False}},
                {'predicate': VIVO.addressPostalCode, 'object': {'literal': True}}],
        'photo': [{'predicate': VITROP.mainImage, 'object': {'literal': False}},
                  {'predicate': VITROP.filename, 'object': {'literal': True}}],
        'abbreviation': [{'predicate': VIVO.abbreviation, 'object': {'literal': True}}],
        'isni': [{'predicate': UFV.isni, 'object': {'literal': True}}],
        'successor': [{'predicate': VIVO.hasSuccessorOrg, 'object': {'literal': False}}],
        'overview': [{'predicate': VIVO.overview, 'object': {'literal': True}}]
    }

    triples = get_org_triples()
    write_triples(triples, filename)
    og = Graph()
    og.parse('__'+filename, format='nt')
    ug = Graph()
    for s, p, o in og:
        ug.add((s, p, o))
    print datetime.now(), 'Graphs ready for processing. Original has ', len(og), '. Update graph has', len(ug)
    org_updates = read_csv(filename, delimiter='\t')
    print datetime.now(), 'Updates ready for processing.  ', filename, 'has ', len(org_updates), 'rows.'
    for row, org_update in org_updates.items():
        uri = URIRef(org_update['uri'])
        if (uri, None, None) not in ug:

            #  If the org uri can not be found in the update graph, make a new URI ignoring the one in the spreadsheet
            #  if any, and add the URI to the update graph.  Reaming processing is unchanged.  Since the new uri does
            #  not have triples for the columns in the spreadsheet, each will be added

            uri_string = get_vivo_uri()
            print "Adding an organization for row", row, ".  Will be added at", uri_string
            uri = URIRef(uri_string)
            ug.add((uri, RDF.type, FOAF.Organization))

        for column_name, column_def in column_defs.items():
            if len(column_def) == 1:

                vivo_object = ug.value(uri, column_def[0]['predicate'], None, any=True)
                vivo_string = str(vivo_object)

                # Handle enumerations

                if 'enum' in column_def[0]['object']:
                    column_string = eval(column_def[0]['object']['enum']).get(org_update[column_name], None)
                    if column_string is None:
                        print row, column_name, "INVALID", org_update[column_name], "not found in", column_def[0]['object']['enum']
                        continue
                    print row, column_name, column_string
                else:
                    column_string = org_update[column_name]

                # Handle filters

                if 'filter' in column_def[0]['object']:
                    was_string = column_string
                    column_string = eval(column_def[0]['object']['filter'])(column_string)
                    if was_string != column_string:
                        print row, column_name, column_def[0]['object']['filter'], "FILTER IMPROVED", was_string, 'to',\
                            column_string

                # Compare VIVO to Input and update as indicated

                if column_string == '':
                    pass  # No action required if spreadsheet is blank
                elif column_string == 'None':
                    print "Remove", column_name, "from", str(uri)
                    ug.remove((uri, column_def[0]['predicate'], vivo_object))
                elif column_string == vivo_string:
                    pass  # No action required if spreadsheet string is the same as VIVO string
                else:
                    print datetime.now(), 'Update org', uri, column_name, ' from', \
                        vivo_string, 'to', column_string
                    ug.remove((uri, column_def[0]['predicate'], vivo_object))
                    if column_def[0]['object']['literal']:
                        ug.add((uri, column_def[0]['predicate'], Literal(column_string)))
                    else:
                        ug.add((uri, column_def[0]['predicate'], URIRef(column_string)))

    # Write out the triples to be added and subbed in n-triples format

    add = ug - og  # Triples in update that are not in original
    sub = og - ug  # Triples in original that are not in update
    print datetime.now(), "Will add", len(add), "triples and subtract ", len(sub), "triples."
    print datetime.now(), "Triples to add:"
    print add.serialize(format='nt')
    print datetime.now(), "Triples to sub:"
    print sub.serialize(format='nt')
    return len(og)

# Driver program starts here

org_type_data = read_csv("org_types.txt", delimiter=' ')
org_types = {}
org_uris = {}
for row in org_type_data.values():
    org_uris[row['type']] = row['uri']
    org_types[row['uri']] = row['type']
print datetime.now(), org_types

parser = argparse.ArgumentParser()
parser.add_argument("action", help="desired action.  get = get org data from VIVO.  update = update VIVO organ"
                                   "izational data from a spreadsheet", default="update", nargs='?')
parser.add_argument("filename", help="name of spreadsheet containing org data to be updated in VIVO",
                    default="sv_orgs.txt", nargs='?')
args = parser.parse_args()

if args.action == 'get':
    n_orgs = do_get_orgs(args.filename)
    print datetime.now(), n_orgs, "Organizations in", args.filename
elif args.action == "update":
    n_orgs = do_update_orgs(args.filename)
else:
    print datetime.now(), "Unknown action.  Try sv_orgs -h for help"

