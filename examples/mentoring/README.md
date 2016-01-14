# Managing mentoring relationships in VIVO

Professional mentoring, graduate or undergrauate degree mentoring, 
other types of person-to-person mentoring relationships.

To enter a mentoring relationship, there are seven attributes

1.  advisee -- entered by orcid from list in enumeration
1.  The type of mentoring relationship.  fac, graduate, undergrad, postdoc.  Put a "1" in the column corresponding
to the type of mentoring relationship.  Put a '0' in the columns that do not represent the mentoring relationship.
1.  advisee -- entered by orcid from list in enumeration
1.  subject_area -- entered by name from list in enumeration.  if more than one, separate with the intra field
delimiter
1.  degree -- entered by name from list in enumeration
1.  start -- the start year for the mentoring relationship -- entered by value from list in enumeration
1.  end -- the end year for the mentoring relationship -- entered by value from list in enumeration

As with everything in Simple VIVO, the attributes are optional.  For any particular advising relationship,
enter as many attribute values as you have.  It is straightforward to update the advising relationship
with additional attributes in the future.

## Enumerations

1. `orcid_enum.txt` -- used to identify possible advisors and advisees
1. `concept_enum.txt` -- used to identify possible subject areas for the advising relationship
1. `degree_enum.txt` -- used to identify the degree if mentoring is related to obtaning a degree
1. `date_enum.txt` -- used to list the dates by year to indicate start and end

## Adding and Updating mentoring relationships

1. Update the enumerations using `python make_enum.py`
1. Get the existing mentoring relationships from VIVO using `python sv.py -a get`
1. Edit the mentoring relationships as needed -- correcting values as needed, adding values to existing
mentoring relationships, and adding new mentoring relations.  To add new mentoring relationships, add a row to the
spreadsheet, leave the uri column blank, and add as many attributes as you have for the new relationship.
All the attributes you add should be found in the appropriate enumeration (see above).  If the value
you specify is not found, it will not be added.  To add new values, first add them to VIVO, then update
the enumerations, then add them to the mentoring relationship.
1. Update VIVO with your improved spreadsheet using `python -a update`

Repeat these steps as needed to add additional mentoring relationships to VIVO.

