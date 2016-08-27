# PubMed Utilities

PubMed is a common source of bibliographic information for VIVO.  

The following capabilities are in development for the Pump:

1. Given an author, find all the papers in PubMed for that author (using the Harvard Catalyst web service)
1. Given a PubMed ID, retreive the paper citation information from PubMed (using Entrez)
1. Given paper citation information, add the papers to VIVO (using the Pump)
1. Have a Pump handler that bundles the three functions above into a single handler -- given an author, put
their PubMed papers in VIVO.  As with all Pump functionality, this will be done as an update -- existing 
papers will be updated with the information most recently retrieved from Pubmed.

## Status

First two tasks are complete.  

`get_catalyst_pmid` returns a list of PubMed Ids for that author using the Catalyst 
web service

`get_pubmed_paper` returns a simple dictionary of metadata from PubMed about the paper using Entrez

Next up is a pump-based update of VIVO data regarding the publication, followed by a handler for 
loading publications as a handler service when updating VIVO from a spreadsheet of people