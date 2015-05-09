# UF Person Ingest

Intended to be a weekly process to update information in VIVO about UF People.  Here's what's updated:

1. The population of people.  All UF business rules are followed regarding who should be in VIVO and how they 
should be represented.  Some rules (to be expanded)
    1. Qualifying type of person
    1. Does not have privacy flags that would prevent inclusion
1. The status of people -- UFCurrentEntity asserted if the person has a current relationship with VIVO.  The assertion 
is removed if the person is not associated with UF.  If the assertion is removed, contact information and preferred
title is also removed.
1. The contact information for people.  Includes their preferred title and UF Home Department (a UF extension).

In previous UF ingests, positions were handled in a single ingest along with people.  Now there is an ingest 
focused on people and a separate ingest focused on positions.

## Process
The steps below ingest data into UF VIVO

1. Review and update the following input files
    1.  *position_data.csv* -- the weekly pay list from UF.  All people paid by the university.  Abut 40K records
    1.  contact_data.txt -- UF directory data for all UFIDs.  2M records
    1.  deptid_exceptions.txt -- patterns of excluding deptids.
    1.  position_exceptions.txt -- these positions will not be included in VIVO
    1.  salary_plan_exception_filter.txt -- salary plans not on this list are excluded from VIVO
    1.  *privacy_data.txt* -- UF directory privacy flag data for all UFIDs.  2M records
    1.  *ufid_exceptions.txt* -- ufids that are exempt from automatic update
    1.  uri_exceptions.txt -- uris that are exempt from automatic update
1. Run create_shelves to update the shelve versions of these files
1. Run the chain of filters to prepare data for the pump

    cat position_data.csv | python ufid_exception_filter.py >smaller_data.txt
    
1. Inspect the uf_person_data.txt
1. Run the pump