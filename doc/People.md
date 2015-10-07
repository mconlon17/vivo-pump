Each person in VIVO has contact information and other identifying information as expected.

This Simple VIVO example supports 19 attributes for each person.  Each one is optional.

1. display_name
1. orcid -- enter the person's orcid id in the form nnnn-nnnn-nnnn-nnnn
1. types -- enter the person's type(s) using the abbreviations in the `person_types.txt` enumeration.  
`fac` for faculty, `pd` for postdoc, etc.
1. research_areas -- enter the person's research area(s) using the 
1. overview -- enter a plain text overview for the person.  Do not cut and paste from Microsoft Word.
1. name_prefix -- name prefix such as "Dr"
1. first_name -- person's first name
1. middle_name -- person's middle name
1. last_name  -- person's last name
1. name_suffix -- person's name suffix such as "Jr" or "III"
1. title -- person's title
1. phone -- person's primary phone number
1. email -- person's primary email
1. home_page -- person's home page URL
1. street_address -- mailing address street for the person
1. city -- mailing address city
1. state -- mailing address state or province
1. zip -- mailing address postal code
1. country -- mailing address country

As with everything in Simple VIVO, the attributes are optional.  For any particular person,
enter as many attribute values as you have.  It is straightforward to update the person
with additional attributes in the future.

## Enumerations

1. `concept_enum.txt` -- used to list possible subject areas for the advising relationship
1. `person_types.txt` -- used to list possible person types with abbreviations for each

## Adding and Updating people

1. Update the enumerations using `python make_enum.py`
1. Get the existing people from VIVO using `python sv.py -a get`
1. Edit the people as needed -- correcting values as needed, adding values to people in the spreadsheet, 
and adding new people.  To add new a new person, add a row to the
spreadsheet, leave the uri column blank, and add as many attributes as you have for the person.
All the attributes you add should be found in the appropriate enumerations (see above).  If the value
you specify is not found, it will not be added.  To add new values to enumerations, first add them to VIVO, 
then update the enumerations, then add them to the person.
1. Update VIVO with your improved spreadsheet using `python -a update`

Repeat these steps as needed to add additional mentoring relationships to VIVO.