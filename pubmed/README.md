# PubMed Utilities

PubMed is a common source of citation information for VIVO.  

The following capabilities are in development for the Pump:

1. Given an author, find all the papers in PubMed for that author (using the Harvard Catalyst web service)
1. Given a list of PubMed IDs for papers, retreive the paper citation information from PubMed (using Entrez)
1. Given paper citation information, add the papers to VIVO.
1. Have a Pump handler that bundles the three functions above into a single handler -- given an author, put
their PubMed papers in VIVO.  As with all Pump functionality, this will be done as an update -- existing 
papers will be updated with the information most recently retrieved from Pubmed.