#!/usr/bin/env/python

"""
    sv.py: Simple VIVO

    Uses the VIVO Pump to provide data management services for VIVO.  Tabular data is mapped by the pump in and out
    of VIVO.

    Produce a spreadsheet from VIVO that has the entities and attributes ready for editing and updating

    Inputs:  spreadsheet containing updates and additions.  Definition file containing maps to/from columns to
        VIVO objects.  Enumeration tables for translating spreadsheet values to VIVO values and back.  VIVO for
        current state. Config file with parameters describing VIVO and the pump actions.
    Outputs:  spreadsheet with current state.  VIVO state changes. stdout with date times and messages.

    See CHANGELOG.md for history

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.05"

from datetime import datetime
import argparse
import ConfigParser
from pump import Pump

# Simple VIVO uses three sources for parameters to control its actions.  The _last_ value found is the value that
# is used
# 1. Defaults in the code.  These defaults are coded for each parameter in the add_argument calls below
# 2. Values in the config file.  sv.py will read a config file and set the values of the parameters
# 3. Command line parameters
#
#  Program defaults are overwritten by config file values which are overwritten by command line parameters.  Each
#  parameter is handled independently of the others.  So one parameter might be set by the command line, another
#  by program defaults (because it was unspecified on the command line and was not specified in the config file)
#  and a third parameter's value might come from the config file, overwriting the program default and left unspecified
#  on the command line

print datetime.now(), "Start"
program_defaults = {
    'action': 'summarize',
    'defn': 'pump_def.json',
    'inter': '\t',
    'intra': ';',
    'username': 'vivo_root@school.edu',
    'pwd': 'password',
    'rdfprefix': 'pump',
    'queryuri': 'http://localhost:80/vivo/api/sparql_query',
    'uriprefix': 'http://vivo.school.edu/individual/',
    'src': 'pump_data.txt',
    'config': 'sv.cfg',
    'verbose': False,
    'nofilters': False
}

parser = argparse.ArgumentParser(description="Get or update row and column data from and to VIVO",
                                 epilog="For more info, see http://github.com/mconlon17/vivo-pump")
parser.add_argument("-a", "--action", help="desired action.  get = get data from VIVO.  update = update VIVO "
                    "data from a spreadsheet. summarize = show def summary. serialize = serial version of the pump",
                    nargs='?')
parser.add_argument("-d", "--defn", help="name of definition file", nargs="?")
parser.add_argument("-i", "--inter", help="interfield delimiter", nargs="?")
parser.add_argument("-j", "--intra", help="intrafield delimiter", nargs="?")
parser.add_argument("-u", "--username", help="username for API", nargs="?")
parser.add_argument("-p", "--pwd", help="password for API", nargs="?")
parser.add_argument("-q", "--queryuri", help="URI for API", nargs="?")
parser.add_argument("-r", "--rdfprefix", help="RDF prefix", nargs="?")
parser.add_argument("-x", "--uriprefix", help="URI prefix", nargs="?")
parser.add_argument("-s", "--src", help="name of source file containing data to be updated in VIVO", nargs='?')
parser.add_argument("-c", "--config", help="name of file containing config data.  Config data overrides program"
                    "defaults. Command line overrides config file values", nargs='?')
parser.add_argument("-v", "--verbose", action="store_true", help="write verbose processing messages to the log")
parser.add_argument("-n", "--nofilters", action="store_true", help="turn off filters")
args = parser.parse_args()

if args.config is None:
    args.config = program_defaults['config']

# Config file values overwrite program defaults

config = ConfigParser.ConfigParser()
conf = {}
config.read(args.config)  # Read the config file from the config file specified in the command line args
for section in config.sections():
    for name, val in config.items(section):
        program_defaults[name] = val

# Non null command line values overwrite the config file values

for name, val in vars(args).items():
    if val is not None:
        program_defaults[name] = val

# And put the final values back in args

for name, val in program_defaults.items():
    vars(args)[name] = val

if args.verbose:
    print datetime.now(), "Arguments\n", vars(args)

p = Pump(args.defn, args.src, args.verbose, args.nofilters, query_parms={'query_uri': args.queryuri,
                                                                         'username': args.pwd, 'password': args.pwd},
         uri_prefix=args.uriprefix)

p.filters = args.nofilters
if args.action == 'get':
    n_rows = p.get(args.src, args.inter, args.intra)
    print datetime.now(), n_rows, "rows in", args.src
elif args.action == 'update':
    [add_graph, sub_graph] = p.update(args.src, args.inter, args.intra)
    add_file = open(args.rdfprefix + '_add.rdf', 'w')
    print >>add_file, add_graph.serialize(format='nt')
    add_file.close()
    sub_file = open(args.rdfprefix + '_sub.rdf', 'w')
    print >>sub_file, sub_graph.serialize(format='nt')
    sub_file.close()

    print datetime.now(), len(add_graph), 'triples to add', len(sub_graph), 'triples to sub'
elif args.action == 'summarize':
    print p.summarize()
elif args.action == 'serialize':
    print p.serialize()
else:
    print datetime.now(), "Unknown action.  Try sv -h for help"
print datetime.now(), "Finish"
