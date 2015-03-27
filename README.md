# The VIVO Pump

A general tool set for managing data in VIVO using data rectangles (rows and columns, including spreadsheets)

The Pump uses a definition file in JSON format that describes the nature of the rows -- entities in VIVO -- and the 
relationship of the columns to the graph of data in VIVO.  Each row/column intersection is an "instruction" to the Pump:

* blank or empty means do nothing
* None means remove any value found in VIVO
* a value means replace the value in VIVO with the value in the rectangle.

The Pump has two major operators:

1. Get -- gets values from VIVO according to the definition and returns a rectangle
1. Update -- uses a rectangle and updates VIVO according to the definition

# Simple VIVO
    
A command line tool using the pump (Simple VIVO) is delivered with the pump.  Simple VIVO supports data management of
VIVO data from a "spreadsheet" -- a delimited file of rows and columns, and a corresponding definition file.  Simple
VIVO supports get and update, along with some reporting operators.  For example:

    sv get org_def.json orgs.txt
    
will use the definition file org_def.json to get data from VIVO and return it in orgs.txt

    sv update person_def.json people.txt
    
will use the definition file person_def.json and the data people.txt to make updates in VIVO

# Additional Features

1.  Enumerations -- each column can have a defined "enumeration" or substitution list that translates to and from codes 
you might find easier to use than internal VIVO codes.
1.  Filters  -- each column can have an automated filter that takes the value in VIVO and "improves" it, providing a 
standardized representation. Phone numbers, for example, may be filtered to insure that each conforms to standard 
formatting.
1.  Handlers (coming soon) permit additional operations to be performed on column values. A photo handler might make
a thumbnail and insure that the original and its thumbnail are placed in the filesystem where VIVO expects.
1.  Set management.  When VIVO supports multiple values for a value -- research areas for a faculty member, for example,
the Pump supports comparing the set of values in VIVO to the set provided in the spreadsheet during and update and
adding and removing as needed to insure that final set in VIVO is the set specificed in spreadsheet.

# Use Cases

1. Enterprise data management of data in VIVO.  The "enterprise" produces data in rectangles -- lists of people who 
work at the institution, lists of holdings in the institutional repository for people at the institution, etc.  These 
rectangles can be used by the Pump to update data in VIVO on an established schedule.
1. Distributed data management.  Definitions can be structured to provide subsets of entities for management at a local
level.  Separate spreadsheets of faculty per college, for example, would allow college offices to manage attributes
locally.
1. Special collections of data in VIVO.  VIVO is often used to track data that is not otherwise available at the 
enterprise level.  VIVO might maintain photographs of each building on campus.  A simple spreadsheet can be 
maintained with the names of the photographs of each building.  As buildings come and go, or photographs improve,
the collection of photos in VIVO can be updated.
1. Data clean up.  Using the get functionality, particular attributes can be retrieved from VIVO for review by a data manager,
and/or automated improvement using filters (see Additional Features).
1. Upgrades.  Use JSON definitions for your current version to pull data out of an old VIVO and into spreadsheets.  Use JSON definitions for the upgraded version to put data from your spreadsheets into your new VIVO.