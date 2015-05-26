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
__version__ = "0.04"

from datetime import datetime
import argparse
import ConfigParser
from pump import Pump

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--action", help="desired action.  get = get data from VIVO.  update = update VIVO "
                    "data from a spreadsheet. summarize = show def summary. serialize = serial version of the pump",
                    default="summarize", nargs='?')
parser.add_argument("-d", "--defname", help="name of definition file", default="pump_def.json", nargs="?")

parser.add_argument("-f", "--filename", help="name of file containing data to be updated in VIVO",
                    default="pump_data.txt", nargs='?')
parser.add_argument("-c", "--config", help="name of file containing config data.  Config data overrides program defaults. "
                    "Command line overrides config file values.",
                    default="sv.cfg", nargs='?')
parser.add_argument("-v", "--verbose", action="store_true", help="write verbose processing messages to the log")
parser.add_argument("-nf", "--nofilters", action="store_false", help="turn off filters")
args = parser.parse_args()
print args

config = ConfigParser.ConfigParser()
config.read(args.config)
for section in config.sections():
    for item, val in config.items(section):
        print section, item, val

#TODO: Fully implement sv.cfg.  All parms available on command line or cfg.  specify cfg name as parm

p = Pump(args.defname)

print datetime.now(), "Start"
p.verbose = args.verbose
p.filters = args.nofilters
if args.action == 'get':
    n_rows = p.get(args.filename)
    print datetime.now(), n_rows, "rows in", args.filename
elif args.action == 'update':
    [n_add, n_sub] = p.update(args.filename)
    print datetime.now(), len(n_add), 'triples to add', len(n_sub), 'triples to sub'
elif args.action == 'summarize':
    print p.summarize()
elif args.action == 'serialize':
    print p.serialize()
else:
    print datetime.now(), "Unknown action.  Try sv -h for help"
print datetime.now(), "Finish"
