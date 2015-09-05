# UF Sponsor Update

Given a file of sponsors, update or add sponsors to VIVO
 
## Method

Use filters to transform the sponsors.txt data into an input file
for updating the sponsor data in VIVO.  UF sponsor data is limited -- label and SponsorID only.

## Filters

1. Manage_columns_filter.py -- replace all columns with columns needed for ingest.  Improve the sponsor organization
name (UF supplies all upper case and abbreviations).  Add uri, remove and type as columns to facilitate data
management
1. unique_sponsorid_filter.py -- remove rows that duplicated sponsorid.  sponsorid should be unique prior to ingest.
1. merge_filter.py -- look up each sponsorid in VIVO and add the uri to the input file

## Columns in the source data

Seven columns result from the filters:

1. name
1. sponsorid
1. type
1. uri
1. remove
1. harvested_by
1. date_harvested

    cat sponsors_small.txt | python manage_columns_filter.py | python unique_sponsorid_filter.py | 
    python merge_filter.py -v > sponsor_update_data_small.txt