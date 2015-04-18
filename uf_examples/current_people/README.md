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

### Step 1.  Remove all UFCurrentEntity assertions



1. Summarize the remove example:

    ```python sv.py summarize remove_current_def.json remove_current.txt```
    
1.  Do a get

    ```python sv.py get remove_current_def.json remove_current.txt```
    
1.  Do an update

    ```python sv.py update remove_current_def.json remove_current.txt```

How it works:  An enum maps UFCurrentEntity to ''.  When a get is performed, the other types are left unchanged, but all 
UFCurrentEntity types are mapped by the enum to ''.  When the update is performed, there are no UFCurrentEntity
assertions in the source, so all of them are removed from VIVO.  Triples are generated to remove all the UFCurrentEntity type assertions.

### Step 2.  Add UFCurrentEntity for people on the pay list

1. Summarize the remove example:

    ```python sv.py summarize add_current_def.json add_current.txt```
     
1.  Do a get

    ```python sv.py get add_current_def.json add_current.txt```
    
1.  Do an update

    ```python sv.py update add_current_def.json add_current.txt```



How it works:  UF keys people by UFID.  An enum converts UFID to VIVO URI.  See ufid_enum.txt.  A second enum
maps Person to Person; UFCurrentEntity.  Anyone person on the pay list is typed as current.  Triples are
generated to add UFCurrentEntity to all the people on the pay list.


## Notes

1. Emeritus faculty not receiving pay are not marked as current.
1. In rare cases, an employee may drop off the pay list only to return in the next pay period.  VIVO reflects the 
institutional data -- the person is marked not current, then marked current.
1. In previous ingest scripts, updating UFCurrentEntity was part of a larger person ingest.  In this implementation,
maintaining UFCurrentEntity is a separate process.
1. current_enum.txt maps the vivo uri for the UFCurrentEntity class to "True".  A data manager can then scan the column
and change True to None if the person is not current, or to blank to leave the VIVO value as is.