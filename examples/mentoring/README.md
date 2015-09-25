# Managing mentoring relationships in VIVO

Chair of committee, professional mentoring, other types of person-to-person scholarly relationships.

To enter a mentoring relationship, there are severn attributes

1.  Mentor -- entered by orcid from list in enumeration
1.  Mentee -- entered by orcid from list in enumeration
1.  Subject area(s) -- entered by name from list in enumeration
1.  Degree candidacy -- entered by name from list in enumeration
1.  Start year -- entered by value from list in enumeration
1.  End year -- entered by value from list in enumeration

As with everything in Simple VIVO, the attributes are optional.  For any particular advising relationship,
enter as many attribute values as you have.  It is straightforward to update the advising relationship
with additional attributes in the future.

## Enumerations

1. `orcid_enum.txt` -- used to list possible advisors and advisees
1. `concept_enum.txt` -- used to list possible subject areas for the advising relationship
1. `degree_enum.txt` -- used to list the possible degrees
1. `date_enum.txt` -- used to list the dates by year to indicate start and end

## Adding and Updating mentoring relationships

1. Update the enumerations using `python make_enum.py`
1. Get the existing mentoring relationships from VIVO using `python sv.py -a get`
1. Edit the mentoring relationships as needed -- correcting values as needed, adding values to existing
mentoring relationships, and adding new mentoring relations.  To add new relationships, add a row to the
spreadsheet, leave the uri column blank, and add as many attributes as you have for the new relationship.
All the attributes you add should be found in the appropriate enumeration (see above).  If the value
you specify is not found, it will not be added.  To add new values, first add them to VIVO, then update
the enumerations, then add them to the mentoring relationship.
1. Update VIVO with your improved spreadsheet using `python -a update`

Repeat these steps as needed to add additional mentoring relationships to VIVO.

