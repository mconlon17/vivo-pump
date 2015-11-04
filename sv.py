#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    sv.py: Simple VIVO

    Uses the VIVO Pump to provide data management service for VIVO.  Tabular data is mapped by the pump in and out
    of VIVO.

    Produce a spreadsheet from VIVO that has the entities and attributes ready for editing and updating

    Inputs:  spreadsheet containing updates and additions.  Definition file containing maps to/from columns to
        VIVO objects.  Enumeration tables for translating spreadsheet values to VIVO values and back.  VIVO for
        current state. Config file with parameters describing VIVO and the pump actions.
    Outputs:  spreadsheet with current state.  VIVO state changes. stdout with date times and messages.

    See CHANGELOG.md for history
"""

from datetime import datetime
from vivopump import get_args
from pump import Pump

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2015 Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.8.4"

#   Simple VIVO uses three sources for parameters to control its actions.  The _last_ value found is the value that
#   is used
#   1. Defaults in the code.  These defaults are coded for each parameter in the add_argument calls below
#   2. Values in the config file.  sv.py will read a config file and set the values of the parameters
#   3. Command line parameters
#
#   Program defaults are overwritten by config file values which are overwritten by command line parameters.  Each
#   parameter is handled independently of the others.  So one parameter might be set by the command line, another
#   by program defaults (because it was unspecified on the command line and was not specified in the config file)
#   and a third parameter's value might come from the config file, overwriting the program default and left unspecified
#   on the command line


def main():
    """
    The main function.  Does the work of Simple VIVO
    :return: None
    """
    print datetime.now(), "Start"
    args = get_args()
    if args.verbose:
        print datetime.now(), "Arguments\n", vars(args)

    #   Create a Pump and use it to perform the requested actions based on arguments

    p = Pump(args.defn, args.src, args.verbose, args.nofilters, args.inter, args.intra, args.rdfprefix,
             query_parms={'queryuri': args.queryuri,
                          'username': args.username,
                          'password': args.password,
                          'prefix': args.prefix,
                          'uriprefix': args.uriprefix})
    if args.action == 'get':
        n_rows = p.get()
        print datetime.now(), n_rows, "rows in", args.src
    elif args.action == 'update':
        [add_graph, sub_graph] = p.update()
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
    elif args.action == 'test':
        print p.test()
    else:
        print datetime.now(), "Unknown action.  Try sv -h for help"
    print datetime.now(), "Finish"

if __name__ == "__main__":
    main()