# UF Person Ingest

Intended to be a weekly process to update information in VIVO about UF People.  Here's what's updated:

1. The population of people.  All UF business rules are followed regarding who should be in VIVO and how they 
should be represented.  Some rules (to be expanded)
    1. Qualifying type of person.  Type of person is derived from type of current position
    1. Does not have privacy flags that would prevent inclusion
    1. Has opted in.  These people are included
    1. Is in a protected department.  People in these departments need to be shown in their parent departments
    1. Is not a person protected from edit.  Some people are protected from edit.  They can be indicated by uid or
uri.  These people are untouched by the person ingest.
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
    1.  *deptid_exceptions_data.txt* -- patterns of deptids with exceptions.  People with home departments matching these 
    patterns re reassigned to home departments as indicated in the deptid_exceptions_data file
    1.  *salary_plan_enum.txt* -- salary plans indicate the type of person. People must have qualifying
salary plans to be included.
    1.  *privacy_data.txt* -- UF directory privacy flag data for all UFIDs.  2M records
    1.  *ufid_exceptions_data.txt* -- ufids that are exempt from automatic update
    1.  *uri_exceptions_data.txt* -- uris that are exempt from automatic update
1. Run create_shelves to update the shelve versions of these files.  Shelves are used for rapid keyed access
1. Run the chain of filters to prepare data for the pump

    cat position_data.csv | python salary_plan_filter.py | python manage_columns_filter.py | python merge_filter.py | 
    python privacy_filter.py | python contact_filter.py | python homedept_assignment_filter.py | 
    python not_current_filter.py | python null_value_filter.py  | 
    python types_filter.py | python ufid_exception_filter.py | 
    python uri_exception_filter.py  >person_update_data.txt
    
1. Inspect the person_update_data.txt
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
1. homedept_assignment_filter -- for homedepts matching patterns in the input file, assign to corresponding home
departments.
1. not_current_filter -- for people no longer at UF, set their working title and UF contact info to None
1. null_value_filter -- replace all values of "NULL" with empty strings.  Enterprise data containing "NULL" indicates
an unknown or missing value.  No change will be made in VIVO.
1. types_filter -- create a multi-valued "types" field from values in VIVO, values in source, and UFCurrentEntity
status.  Result is a delimited field whose values are codes from the people_types.txt file
1. ufid_exception_filter -- blanks the data of people on the exception list.  These people will not be updated
1. uri_exception_filter -- blanks the data of people on the exception list.  These people will not be updated



## Handlers needed

None.  All data management is performed by the filters.  The resulting file is ready for the pump.  The pump handles 
all adds, changes and deletes of people and their contact information based on its processing of person_update_data.txt

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
1. Final filters handle people excluded from editing, setting all their values to blank.  This insures that these
people are not edited by the pump.  We leave them in the person_update_data so that data managers can see them
and apply manual edits to these records if needed.
1. The pump makes the changes requested in person_update_data.txt, creating add and sub rdf

## Testing

See position_data_small.txt for an abbreviated position file which can be used for testing.  Filtering this file 
leads to person_update_data_small.txt.  The sv.cfg file points at the small version and produced person_add.rdf and
person_sub.rdf, which can be inspected to verify the ingest is working as expected.
