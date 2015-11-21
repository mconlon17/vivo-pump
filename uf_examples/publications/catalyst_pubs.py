#!/usr/bin/env/python
"""
    catalyst-pubmed.py -- identify pubmed papers for author using catalyst
                          service
"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2013, University of Florida"
__license__     = "BSD 3-Clause license"


from Bio import Entrez # tools for using NLM databases including pubmed, from biopython
from xml.dom.minidom import parseString # tools for handling XML in python
import vivotools

print "Making titles dictionary"
title_dictionary = vivotools.make_title_dictionary()
print "Dictionary has ",len(title_dictionary),"entries"


# To use pubmed, you need to supply the email address of the person making the request
#
Entrez.email = 'mconlon@ufl.edu'
#
#  to get PubMed publications from the Harvard service, we need a person's email address and name.  Middle can be empty ("")
#
first = "Michael"
middle = ""
last = "Conlon"
email = "mconlon@ufl.edu"
#
# call the Harvard Catalyst service to get a list of PMIDs for this author
#

print "Results for ",first,middle,last,email
result = vivotools.catalyst_pmid_request(first,middle,last,email)

dom = parseString(result) # create a document Object Model (DOM) from the Harvard Catalyst result
#
#  For each PMID in the DOM, grab the ID from the DOM, call Pubmed, display the results
#
for node in dom.getElementsByTagName('PMID'):
    pmid = node.toxml()
    pmid = pmid.replace('<PMID>','')
    pmid = pmid.replace('</PMID>','')
    handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
    records = Entrez.parse(handle)
    for record in records:
        doc = vivotools.document_from_pubmed(record)
        [found,uri] = vivotools.find_title(doc['title'],title_dictionary)
        print
        print found,uri
        print vivotools.string_from_document(doc)

