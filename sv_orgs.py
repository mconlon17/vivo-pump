#!/usr/bin/env/python

"""
    sv_orgs.py: Simple VIVO for Organizations

    Read a spreadsheet and follow the directions to add, update or remove organizations and/or
    organization attributes from VIVO.

    Produce a spreadsheet from VIVO that has the fields ready for editing and updating

    Exceptions are thrown, caught and logged for missing required elements that are missing

    See CHANGELOG.md for history

"""

# TODO: test file with test cases and notes for each
# TODO: Write do_update_orgs using rdflib
# TODO: Support lookup by name or uri

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.2"

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
    SELECT ?uri ?name ?type ?url ?within ?overview ?photo ?abbreviation ?successor ?address1 ?address2 ?city ?state ?zip ?phone ?email ?isni
    WHERE {

        ?uri a foaf:Organization .
        ?uri a ufVivo:UFEntity .
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

# Driver program starts here

org_type_data = read_csv("org_types.txt", delimiter=' ')
org_types = {}
org_uris = {}
for row in org_type_data.values():
    org_uris[row['type']] = row['uri']
    org_types[row['uri']] = row['type']
print org_types

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

