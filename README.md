# The VIVO Pump

A general tool set for managing data in VIVO using data rectangles (rows and columns, including spreadsheets).

The Pump uses a definition file in JSON format that describes the nature of the rows -- entities in VIVO -- and the relationship of the columns to the graph of data in VIVO.  Each row/column intersection is an "instruction" to the Pump:

* blank or empty means do nothing
* None means remove any value found in VIVO
* a value means replace the value in VIVO with the value in the rectangle.

The Pump has two major operators:

1. Get -- gets values from VIVO according to the definition and returns a rectangle
1. Update -- uses a rectangle and updates VIVO according to the definition

# Simple VIVO

Before you can use this tool please install the requirements:

    pip install -r requirements.txt

A command line tool using the pump (Simple VIVO) is delivered with the pump.  Simple VIVO supports data management of
VIVO data from a "spreadsheet" -- a delimited file of rows and columns, and a corresponding definition file.  Simple
VIVO supports get and update, along with some reporting operators.  For example:

    python sv.py -a get -d org_def.json -s orgs.txt
    
will use the definition file org_def.json to get data from VIVO and return it in orgs.txt

    python sv.py -a update -d person_def.json -s people.txt
    
will use the definition file person_def.json and the source data in people.txt to make updates in VIVO

# Additional Features

1.  Enumerations -- each column can have a defined "enumeration" or substitution list that translates to and from codes 
you might find easier to use than internal VIVO codes.
1.  Filters  -- each column can have an automated filter that takes the value in VIVO and "improves" it, providing a 
standardized representation. Phone numbers, for example, may be filtered to insure that each conforms to standard 
formatting.
1.  Set management.  VIVO supports multiple values for many of its attributes a value -- research areas for a faculty 
member, for example. For such attributes, 
the Pump supports comparing the set of values in VIVO to the set provided in the spreadsheet,
adding and removing as needed to insure that final set in VIVO is the set specified in spreadsheet.
1. Remove and merge actions.  A special column named 'action' can be used to specify which entities should be removed and which
should be merged with other entities.
1.  Handlers (coming soon) permit additional operations to be performed on column values. A photo handler might make
a thumbnail and insure that the original and its thumbnail are placed in the filesystem where VIVO expects.

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
the collection of buildings and their photos in VIVO can be updated.
1. Data clean up.  Using the get functionality, particular attributes can be retrieved from VIVO for review by a data 
manager, and/or automated improvement using filters (see Additional Features).
1. Upgrades.  Use JSON definitions for your current version to pull data out of an old VIVO and into spreadsheets.  
Use JSON definitions for the upgraded version to put data from your spreadsheets into your new VIVO.

# Semantic versioning

The Pump is version numbered using semantic versioning.  See http://semver.org.  See the Pump for the current version.
Semantic versioning involves three numeric version numbers:  the major number, the minor number and the patch number.
The major number 0, 1, etc indicates version of the API that are not backward compatible -- your use of the Pump _must_
change if the Pump moves from major version *x* to major version *x+1*.  The minor number indicates additional
functionality that *does not* alter your existing use of the Pump.  Minor versions *do not* cause your use of the 
Pump to change.  You may find that you wish to take advantage of new features offered by the minor version and as a 
result, you choose to alter your use of the Pump.  Patch versions fix bugs.  They do not provide additional
functionality.  Any of these version numbers may increment indefinitely.  In addition, the Pump may use release 
candidates, in which case you will see a version number such as x.y.z-rc1 indicating a release candidate for x.y.z

The Pump currently has a major version number of "0."  This indicates that the Pump is pre-production and that the API
is under development.  Minor version numbers continue to increase as features are added.

# The Pump API

**Note:  This is a first attempt to define the API of the Pump for semantic versioning.  No guarantees.**

The Pump API consists of:

1. The Pump arguments.  All Pump arguments are available as configurable parameters -- 1) accessible from the command
line of simple vivo (`sv`), 2) settable from the config file used by simple vivo and the "filters" you will see in the
examples, and 3) hard coded into the software as defaults to be overridden by the config file and/or command line
parameters.
2.  Pump methods and instance variables.  The instance variables correspond to the arguments described above.  The
methods are used to execute Pump functionality.
3.  The JSON definition file structure.  Structure of the JSON definition file is part of the API.  Semantic versioning 
applies to changes in the structure of definition files used by the Pump.  Features may be added, leading to minor
version number increments.  When existing JSON files must be upgraded, these constitute major version number increments.

The Pump API *does not* include the `vivopump` functions and their calling sequences.  The `vivopump` software is 
provided solely to serve the Pump as ancillary/internal functions of the Pump and may be refactored without altering the 
semantic versioning of the Pump.

# The Pump Wiki

[The Pump Wiki](https://github.com/mconlon17/vivo-pump/wiki) describes the Pump, its API, test cases, its use in 
software, and its use via the command tool Simple VIVO.  Simple VIVO is described in detail -- usage, examples, and
extending examples.  Together, the Pump and Simple VIVO provide a method for standardizing and simplifying data
management in VIVO.

# The Simple VIVO Book

[Simple VIVO](https://www.gitbook.com/book/mconlon17/simple-vivo/details), the book, is available on-line as a free, open access, text.  Managed using GitHub and produced using GitBook, you can contribute to the Simple VIVO book in the same way you would contribute to a GitHub open source project.  The book describes Simple VIVO and the Pump in detail with worked examples.  The Simple VIVO book is available as an on-line hypertext, and as a download PDF, an eBook for iBooks and as a Mobi file for Kindle readers.
