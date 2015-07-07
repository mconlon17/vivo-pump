# UF Publications Ingest

Publications are ingested from a bibtex file each week.  The bibtex file is the result of a query to Thomson
Reuters Web of Knowledge for publications of UF authors over the past seven days.

Five ingests are run from the same input file.  In each case, filters extract the appropriate columns, perform
a match, generate a source file suitable for an update.

1.  Concepts are matched by name
1.  Publishers are matched by name
1.  Journals are matched by ISSN
1.  People are matched using a disambiguation handler.  UF people are matched by name.  Non-UF people are always 
added as stubs
1.  Publications are matched by PMID, DOI or title.

## Filters

TBA

## Handlers

Disambiguation handler takes and author list and generates authorships for UF authors.  Authors that can not be
uniquely identified are listed in a disambiguation report

PubMed handler takes a PubMed ID and supplies the RDF needed to add the paper to VIVO.  The PubMed handler calls the
Disambiguation handler

## Process

1. Obtain a current pubs.bib from TR Web of Knowledge
1. Run bib2csv to create a raw file
1. Run the filters to produce the required input file.  The same input file is used for all five ingests:
1. Add concepts not currently in VIVO
1. Add publishers not currently in VIVO
1. Add journals not currently in VIVO
1. Add people not currently in VIVO
1. Add publications to VIVO
1. Run the pump to create add and sub RDF
1. Add the add RDF and subtract the sub 
1. Inspect the disambiguation report and manually determine which changes must be made and make them in VIVO using
the web interface.  A UF weekly ingest typically involves 120 papers, 360 UF authors, and 20 disambiguations to 
be resolved manually.  Typically takes about an hour.
1. Update appropriate documentation regarding actions and results