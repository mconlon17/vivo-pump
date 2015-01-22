#!/usr/bin/env/python

"""
    sv_orgs.py: Simple VIVO for Organizations

    Read a spreadsheet and follow the directions to add, update or remove organizations and/or
    organization attributes from VIVO.

    Exceptions are thrown, caught and logged for missing required elements that are missing

    See CHANGELOG.md for history

"""

# TODO: test file with test cases and notes for each
# TODO: Finish get
# TODO: Write do_update_orgs using rdflib
# TODO: Support lookup by name or uri

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.0"

from vivofoundation import read_csv
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

    query = """
    SELECT ?uri ?name ?type ?url ?within ?overview ?photo ?abbreviation ?successor ?address ?phone ?email ?isni
    WHERE {

       ?uri a foaf:Organization .
       ?uri a ufVivo:UFEntity .
       ?uri rdf:type ?type .
       FILTER (?type != foaf:Organization && ?type != foaf:Agent && ?type != owl:Thing && ?type != ufVivo:UFEntity)
       ?uri rdfs:label ?name .
       OPTIONAL { ?uri vivo:webpage ?url . }
       OPTIONAL { ?uri vivo:subOrganizationWithin ?within . }
       OPTIONAL { ?uri vivo:overview ?overview . }
       OPTIONAL { ?uri vitro:mainImage ?photo . }
       OPTIONAL { ?uri vivo:abbreviation ?abbreviation . }
       OPTIONAL { ?uri vivo:hasSuccessorOrganization ?successor . }
       OPTIONAL { ?uri vivo:mailingAddress ?address . }
       OPTIONAL { ?uri vivo:phoneNumber ?phone . }
       OPTIONAL { ?uri vivo:email ?email . }
       OPTIONAL { ?uri ufVivo:isni ?isni . }

    }
    ORDER BY ?name
    """

    org_result_set = vivo_sparql_query(query, debug=True)  # show the encoded query
    print org_result_set
    
    orgs = {}
    
    for binding in org_result_set['results']['bindings']:

        uri = binding['uri']['value']
        if uri not in orgs:
            orgs[uri] = {}
    
        #  Each property is either single-valued, multi-valued, and/or de-referenced.  We're not
        #  not ready for de-referenced yet.  That will require more complex SPARQL

        # Single valued attributes.  If data has more than one value, use the last value found
    
        for name in ('uri', 'name', 'url', 'overview', 'photo', 'abbreviation', 'address', 'phone', 'email', 'isni'):
            if name in binding:
                orgs[uri][name] = binding[name]

        # multi-valued attributes.  Collect all values into lists
        
        for name in ('successor', 'within', 'type'):
            if name in binding:
                if name in orgs[uri]:
                    orgs[uri][name].append(binding[name])
                else:
                    orgs[uri][name] = [binding[name]]

    print orgs

    # Write out the file
    # TODO: Add header line
    # TODO: get order of fields right

    outfile = codecs.open(filename, mode='w', encoding='ascii', errors='xmlcharrefreplace')

    for uri in sorted(orgs.keys()):
        for name in ('uri', 'name', 'url', 'overview', 'photo', 'abbreviation', 'address', 'phone', 'email', 'isni'):
            if name in orgs[uri]:
                val = orgs[uri][name]['value'].replace('\n', ' ').replace('\r', ' ')
                outfile.write(val)
            outfile.write('\t')
        for name in ('successor', 'within', 'type'):
            if name in orgs[uri]:
                for x in orgs[uri][name]:
                    val = x['value'].replace('\n', ' ').replace('\r', ' ')
                    outfile.write(val)
                    outfile.write(';')
            outfile.write('\t')
        outfile.write('\n')

    outfile.close()
    
    return len(orgs)

# Driver program starts here

parser = argparse.ArgumentParser()
parser.add_argument("action", help="desired action.  get = get org data from VIVO.  update = update VIVO organ"
                                   "izational data from a spreadsheet", default="update", nargs='?')
parser.add_argument("filename", help="name of spreadsheet containing org data to be updated in VIVO",
                    default="sv_orgs.txt", nargs='?')
args = parser.parse_args()

if args.action == 'get':
    print "will get org data from VIVO"
    norgs = do_get_orgs(args.filename)
    print norgs, "Organizations in", args.filename
elif args.action == "update":
    orgs = read_csv(args.filename, delimiter="\t")
    print orgs
else:
    print "Unknown action.  Try sv_orgs -h for help"

