# Managing Grants in Simple VIVO

Grants are a bit more complex than some of the other entities we have been managing using Simple VIVO.  Grants
have the following columns. Each is optional.

1. Local award ID -- that is, what number, or other identifier, does your institution give this grant?
1. Title
1. Direct costs -- all years
1. Total award amount -- all years, direct plus indirect
1. Principal investigators -- one or more principal investigators. Identified by enumeration.
1. Co-principal investigators -- any number of co-principal investigators. Identified by enumeration.
1. Investigators -- any number of additional investigators. Identified by enumeration.
1. Concepts -- any number of concepts identifying subject areas for the grant. Identified by enumeration.
1. Start date in the form yyyy-mm-dd. Identified by enumeration.
1. End date in the form yyyy-mm-dd. Identified by enumeration.
1. Administering unit. Identified by enumeration.
1. Sponsor. Identified by enumeration.
1. Sponsor's award ID -- how does the sponsor refer to this grant?  The National Institutes of Health in the US, for
example, gives its grants award IDs that look like R01DK22343
1. URI in VIVO.  Blank if you are adding the grant.  VIVO URI returned by get.

## Enumerations

Simple VIVO for grants uses several enumerations to identify data already in your VIVO, that may be linked to one
of your grants.  Each enumeration is made or updated using `make_enum.py` as described below.

1. `concept_enum.txt` lists the concepts in your VIVO by name
1. `date_enum.txt` lists the year-month-day dates in your VIVO by date value
1. `dept_enum.txt` lists your organizations by name
1. `orcid_enum.txt` lists your investigators by ORCID.  ORCID is used to identify your investigators.  
Each should have an ORCID, and the ORCID for each investigator should be in your VIVO.  See examples/people for
adding ORCID to people.
1. `sponsor_enum.txt` lists the sponsors (funding organizations) in your VIVO by name.

## The Basic steps

1. Use `make_enum.py` to prepare the enumerations for grants

    `python make_enum.py`

1. Use get to retrieve the grants from your VIVO to a spreadsheet

    `python sv.py -a get`
    
1. Edit your spreadsheet to improve your grant data, and add new grants

1. Use update to put your improved grant data back in VIVO

    `python sv.py -a update`
    
1. Repeat the steps each time you wish to improve your grant data

