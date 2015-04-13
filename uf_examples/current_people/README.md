# UF Current People

UF has two type extensions to track UF things

* UFEntity -- entities with this type are "UF" things -- used for people and orgs.  UFEntity is the UF 
institutional class.
* UFCurrentEntity -- entities with this type are at UF now. A sub-class of UFEntity, that is all UFCurrentEntity are 
UFEntity.

## Maintaining UFCurrentEntity for People

Each week, the VIVO team runs a query of the UF Enterprise Data warehouse to access the "pay list" -- the list of all
people receiving compensation from UF during the preceding pay period.  People on this list will have UFCurrentEntity.
People not on this list will not.

Notes:

1. Emeritus faculty not receiving pay are not marked as current.
1. In rare cases, an employee may drop off the pay list only to return in the next pay period.  VIVO reflects the 
institutional data -- the person is marked not current, then marked current.
1. In previous ingest scripts, updating UFCurrentEntity was part of a larger person ingest.  In this implementation,
maintaining UFCurrentEntity is a separate process.
1. current_enum.txt maps the vivo uri for the UFCurrentEntity class to "True".  A data manager can then scan the column
and change True to None if the person is not current, or to blank to leave the VIVO value as is.