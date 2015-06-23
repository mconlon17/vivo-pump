# UF Publications Ingest

Publications are ingested from a bibtex file each week.  The bibtex file is the result of a query to Thomson
Reuters Web of Knowledge for publications of UF authors over the past seven days.

Names of authors are matched to 

## Filters

TBA

## Handlers

Disambiguation handler takes and author list and generates authorships for UF authors.  Authors that can not be
uniquely identified are listed in a disambiguation report

PubMed handler takes a PubMed ID and supplies the RDF needed to add the paper to VIVO.  The PubMed handler calls the
Disambiguation handler

## Process

1. Obtain a current pubs.bib from TR Web of Knowledge
1. Run the filters to produce the required input file
1. Run the pump to create add and sub RDF
1. Add the add RDF and subtract the sub 
1. Inspect the disambiguation report and manually determine which changes must be made and make them in VIVO using
the web interface.  A UF weekly ingest typically involves 120 papers, 360 UF authors, and 20 disambiguations to 
be resolved manually.  Typically takes about an hour.
1. Update appropriate documentation regarding actions and results