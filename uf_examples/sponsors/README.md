# UF Sponsor Update

Given a file of sponsors, update or add sponsors to VIVO
 
## Method

Use filters to transform the sponsors.txt data into an input file
for updating the sponsor data in VIVO.  Sponsor data is limited -- label and SponsorID only.

## Filters

TBA

## Attributes

Three attributes are managed

1. name
1. localSponsorID
1. type

    cat sponsors.txt | python manage_columns_filter.py | python unique_sponsorid_filter.py | 
    python merge_filter.py > sponsor_update_data.txt