# UF Publications Ingest

Publications are ingested from a bibtex file each week.  The bibtex file is the
result of a query to **Thomson Reuters Web of Knowledge** for publications of UF
authors over the past seven days.

Four ingests are run from the same input file.  In each case, filters extract
the appropriate columns, perform a match, generate a source file suitable for
an update.

1.  Publishers are matched by name.
2.  Journals are matched by ISSN.
3.  People are matched using a disambiguation handler.  UF people are matched
    by name.  Non-UF people are always added as stubs.
4.  Publications are matched by PMID, DOI or title.

## Filters (located in the filters/ folder)

1. `author_match_filter.py`    -- For uf authors, find uri, for non-uf authors,
                                     assume add.
2. `author_prep_filter.py`     -- Prepare columns for authors.
3. `bib2csv_filter.py`         -- Read a bibtex file and output a CSV.
                                    No edits to the bibtex.
4. `journal_columns_filter.py` -- Columns needed to manage journals
5. `journal_match_filter.py`   -- Match the journals in the source to the 
                                    journals in VIVO
6. `pub_columns_filter.py`     -- Select the columns for the publications ingest
7. `pub_match_filter.py`       -- Match publications to existing pubs in VIVO.
                                    Match authors. Match journals
8. `publisher_columns_filter.py` -- Results in the columns needed for the
                                    publisher update.
9. `publisher_match_filter.py` -- Match publishers in source to publishers in
                                    VIVO.  Matches are discarded. Only new 
                                    publishers make it through the filter.
10. `unique_issn_filter.py` -- Remove duplicate issn
11. `unique_name_filter.py` -- Remove duplicate publisher names.



## Handlers

1. Disambiguation handler takes and author list and generates authorships for
    UF authors.  Authors that can not be uniquely identified are listed in a
    disambiguation report.
2. PubMed handler takes a PubMed ID and supplies the RDF needed to add the paper
    to VIVO.  The PubMed handler calls the Disambiguation handler.

## Process

0. Make a copy of the example files and crate an output folder where we will
store the generated files:

    mkdir config data_in data_out
    cp -R config_example/ config
    cp -R data_in_example/ data_in


0. Obtain a current bibtext file from Thomson Reuters Web of Knowledge
1. Add **publishers** not currently in VIVO

        cat data_in/tr_07_03_2015_wk_fin.bib \
            | python filters/bib2csv_filter.py \
            | python filters/publisher_columns_filter.py \
            | python filters/unique_name_filter.py \
            | python filters/publisher_match_filter.py -c sv_publishers.cfg \
            > data_out/publisher_update_data.txt

    Then run:

        sv -a update \
            -d publisher_def.json \
            -c config/sv_publishers.cfg \
            -s data_out/publisher_update_data.txt

    Then using the files generated in `data_out` folder:

    1. Verify `publisher_sub.rdf` is zero length
        (once added a publisher should be never removed)
    2. Add `publisher_add.rdf` to VIVO

2. Add **journals** not currently in VIVO

        cat data_in/tr_07_03_2015_wk_fin.bib \
            | python filters/bib2csv_filter.py \
            | python filters/journal_columns_filter.py \
            | python filters/unique_issn_filter.py \
            | python filters/journal_match_filter.py \
            > data_out/journal_update_data.txt

    Then run:

       sv -c config/sv_journals.cfg

    Then using the files generated in `data_out` folder:

    1. Add `journal_add.rdf` to VIVO
    2. Sub `journal_sub.rdf` from VIVO

3. Add **people** not currently in VIVO

        cat data_in/tr_07_03_2015_wk_fin.bib \
            | python filters/bib2csv_filter.py \
            | python filters/author_prep_filter.py \
            | python filters/author_match_filter.py \
            > data_out/author_update_data.txt

    Then run:

        sv -a update \
            -d author_def.json \
            -c config/sv_authors.cfg \
            -s data_out/author_update_data.txt

    Then using the files generated in `data_out` folder:

        Add `author_add.rdf` to VIVO
        Sub `author_sub.rdf` from VIVO

4. Add **publications** to VIVO

        cat data_in/tr_07_03_2015_wk_fin.bib \
            | python filters/bib2csv_filter.py \
            | python filters/pub_columns_filter.py \
            | python filters/pubmed_match_filter.py \
            | python filters/pub_match_filter.py \
            > data_out/pub_update_data.txt

    Then run:

        sv -c config/sv_pubs.cfg

    Then using the files generated in `data_out` folder:

    1. Add `pub_add.rdf` to VIVO
    2. Sub `pub_sub.rdf` from VIVO

5. Inspect the disambiguation report and manually determine which changes must
    be made and make them in VIVO using the web interface.  A UF weekly ingest
    typically involves 120 papers, 360 UF authors, and 20 disambiguations to
    be resolved manually.  Typically takes about an hour
6.  Update appropriate documentation regarding actions and results
