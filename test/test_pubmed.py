#!/usr/bin/env/python
# coding=utf-8
"""
    test_improve.py -- Test cases for improve
"""

import unittest

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "0.1"


class CatalystTestCase(unittest.TestCase):
    def test_get_catalyst_pmids_xml(self):
        from pubmed.pubmed import get_catalyst_pmids_xml
        first = 'David'
        middle = 'R'
        last = 'Nelson'
        email_list = ['drnelson@ufl.edu']
        result = get_catalyst_pmids_xml(first, middle, last, email_list)
        print result
        self.assertTrue(len(result) > 0)

    def test_get_catalyst_pmids(self):
        from pubmed.pubmed import get_catalyst_pmids
        first = 'David'
        middle = 'R'
        last = 'Nelson'
        email_list = ['drnelson@ufl.edu']
        result = get_catalyst_pmids(first, middle, last, email_list)
        print len(result), "papers found"
        self.assertTrue(len(result) > 0)


class EntrezTestCase(unittest.TestCase):
    def test_get_pubmed_entrez(self):
        from pubmed.pubmed import get_pubmed_entrez
        from types import GeneratorType
        pmid = '21916639'
        result = get_pubmed_entrez(pmid)
        self.assertTrue(isinstance(result, GeneratorType))

    def test_get_pubmed_paper(self):
        from pubmed.pubmed import get_pubmed_paper
        from json import dumps
        pmid = '21916639'
        result = get_pubmed_paper(pmid)
        print dumps(result, indent=4)
        self.assertTrue(len(result) > 0)



