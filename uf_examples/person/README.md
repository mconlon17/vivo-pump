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
    1.  *contact_data.txt* -- UF directory data for all UFIDs.  2M records
    1.  *deptid_exceptions.txt* -- patterns of excluding deptids.
    1.  *salary_plan_enum.txt* -- salary plans indicate the type of person. People must have qualifying
salary plans to be included.
    1.  *privacy_data.txt* -- UF directory privacy flag data for all UFIDs.  2M records
    1.  *ufid_exceptions.txt* -- ufids that are exempt from automatic update
    1.  *uri_exceptions.txt* -- uris that are exempt from automatic update
1. Run create_shelves to update the shelve versions of these files
1. Run the chain of filters to prepare data for the pump

    cat position_data.csv | python salary_plan_filter.py | python manage_columns_filter.py | python merge_filter.py | 
    python privacy_exception_filter.py | python contact_filter.py | python ufid_exception_filter.py |
    python uri_exception_filter.py >person_update_data.txt
    
1. Inspect the uf_person_data.txt
1. Run the pump

## Filters used

1. salary_plan_filter -- only people having salary plans in the salary_plan_enum.txt file can be added to VIVO
1. manage_columns_filter -- remove columns in the source that will not be used by the pump.  Add columns to the source
that will be used
1. merge_filter -- merge results from VIVO and source to gather all UF people and apply source updates to people
already in VIVO.  Assigns a uri to source people in VIVO.  Adds values to the current column to indicate whether a 
particular person is in the source (current) or not
1. privacy_exception_filter.py  -- if privacy flags are set, new person will not be added
1. contact_filter.py -- contact data columns are added for all ufids found in the contact data
1. ufid_exception filter -- blanks the data of people on the exception list.  These people will not be updated
1. uri_exception filter -- blanks the data of people on the exception list.  These people will not be updated

## Handlers needed

Handlers perform tasks complex tasks and provide a way to customize the operation of the Pump.  The UF person ingest
uses two handlers:

1. deptid_handler -- some deptids are protected from disclosure.  No person may be listed as having such a deptid as 
their home department, nor may any position appear in these departments.  The handler reads a set of deptid
patterns, reassigns home departments to parent orgs.
1. closeout_handler -- when a person has UFCurrentEntity removed, they are closed out by this handler.  Working title
and contact data are removed and UF positions acquire end dates.

## How it works

Several filters shape the data from what UF provides to what is needed for the pump.

1. merge_filter.py extracts the ufid and their uri from VIVO.  These are match-merged to the data coming from
uf.  There are three cases:
    1. The ufid is in VIVO and the source.  Data will be updated in VIVO, the person will be marked UFCurrentEntity
    1. The ufid is in VIVO, but not in the source.  UFCurrentEntity will be removed
    1. The ufid is not in VIVO, is in the source.  Person will be added to VIVO with a new uri.  Person will be marked 
    UFCurrentEntity
1. Subsequent filters apply to all people, not just those in the current source.  This ensures that if people change
their privacy flags, or end up on an improved exception list, they are removed or added to VIVO as needed.