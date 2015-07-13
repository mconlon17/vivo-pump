# UF Publications Ingest

Publications are ingested from a bibtex file each week.  The bibtex file is the result of a query to Thomson
Reuters Web of Knowledge for publications of UF authors over the past seven days.

Four ingests are run from the same input file.  In each case, filters extract the appropriate columns, perform
a match, generate a source file suitable for an update.

1.  Publishers are matched by name
1.  Journals are matched by ISSN
1.  People are matched using a disambiguation handler.  UF people are matched by name.  Non-UF people are always 
added as stubs
1.  Publications are matched by PMID, DOI or title.

## Filters

1. bib2csv_filter.py -- read a bibtex file and output a CSV.  No edits to the bibtex.
1. publish_columns_filter.py -- results in the columns needed for the publisher update
1. unique_name_filter.py -- remove duplicate publisher names
1. match_publishers.py -- matches publishers in source to publishers in VIVO.  Matches are discarded.  Only
new publishers make it through the filter
1. journal_columns_filter.py -- columns needed to manage journals
1. unique_issn_filter.py -- remove duplicate issn
1. match_journals.py -- match the journals in the source to the journals in VIVO

## Handlers

Disambiguation handler takes and author list and generates authorships for UF authors.  Authors that can not be
uniquely identified are listed in a disambiguation report

PubMed handler takes a PubMed ID and supplies the RDF needed to add the paper to VIVO.  The PubMed handler calls the
Disambiguation handler

## Process

1. Obtain a current bib from TR Web of Knowledge     
1. Add publishers not currently in VIVO

        cat tr_07_03_2015_wk_fin.bib | python bib2csv_filter.py | python publisher_columns_filter.py | 
        python unique_name_filter.py | python match_publishers_filter.py > publisher_update_data.txt
    
    Then
    
        sv -c sv_publishers.cfg
    
    Then
    
    Verify publisher_sub.rdf is zero length
    
    Add publisher_add.rdf to VIVO
    
1. Add journals not currently in VIVO

        cat tr_07_03_2015_wk_fin.bib | python bib2csv_filter.py | python journal_columns_filter.py | 
        python unique_issn_filter.py | python match_journals_filter.py > journal_update_data.txt
        
   Then
   
       sv -c sv_journals.cfg
       
   Add journal_add.rdf to VIVO
   Sub journal_sub.rdf from VIVO
    
1. Add people not currently in VIVO

        cat tr_07_03_2015_wk_fin.bib | python bib2csv_filter.py | python author_prep_filter.py | 
        python match_authors_filter.py > author_update_data.txt

1. Add publications to VIVO
1. Inspect the disambiguation report and manually determine which changes must be made and make them in VIVO using
the web interface.  A UF weekly ingest typically involves 120 papers, 360 UF authors, and 20 disambiguations to 
be resolved manually.  Typically takes about an hour.
1. Update appropriate documentation regarding actions and results