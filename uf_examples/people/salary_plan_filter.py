#!/usr/bin/env/python

"""
    salary_plan_filter.py -- include only people with a qualifying salary plan
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.01"

import sys

from pump.vivopump import read_csv_fp, read_csv, write_csv_fp

plan_data = read_csv('salary_plan_enum.txt', delimiter='\t')
vivo_plans = [plan_data[x]['short'] for x in plan_data if plan_data[x]['vivo'] != "None"]  # list of qualifying plans
data_in = read_csv_fp(sys.stdin)
print >>sys.stderr, 'Data in', len(data_in)
data_out = {}
qualify = 0
do_not_qualify = 0
for row, data in data_in.items():
    new_data = dict(data)
    if new_data['SAL_ADMIN_PLAN'] in vivo_plans:
        qualify += 1
        new_data['types'] = new_data['SAL_ADMIN_PLAN']
        data_out[row] = new_data
    else:
        do_not_qualify += 1

print >>sys.stderr, 'Qualify', qualify
print >>sys.stderr, 'Do not qualify', do_not_qualify
print >>sys.stderr, 'Data out', len(data_out)
write_csv_fp(sys.stdout, data_out)





