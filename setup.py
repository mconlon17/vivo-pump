#!/usr/bin/env/python

"""
    setup.py: The VIVO Pump

    Install the VIVO Pump, a tool for getting and updating VIVO data to and from spreadsheets
"""

from distutils.core import setup

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2016 Michael Conlon"
__license__ = "New BSD License"
__version__ = "0.8.7"


setup(
    name='vivo-pump',
    version='0.8.7',
    url='https://github.com/mconlon17/vivo-pump',
    license='New BSD License',
    author='Michael Conlon',
    author_email='mconlon@duraspace.org',
    description='Use CSV files to update data in VIVO and get data from VIVO.  All semantics are externalized in'
        'JSON format definition files.',
    py_modules=['pump.vivopump', 'pump.pump'],
    requires=['rdflib(>=4.2.1)', 'SPARQLWrapper(>=1.6.4)', 'bibtexparser(>=0.6.0)'],
)
