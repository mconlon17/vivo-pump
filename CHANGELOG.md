# Changelog for sv_org.py

* **2015-01-20** Code frame and to do list
* **2015-01-21** argparse for command line, read tab-delimited text file from args, first output tab delimited file 
from VIVO
* **2015-01-22** get is complete
* **2015-01-27** General data structure for updates and updates.  Now handles datatype and lang.  Handles updates 
and adds. Handles all six value conditions.
* **2015-01-29** Enumerations handled.  Filters handled.
* **2015-01-30** 0.29 Data structure enhanced to indicate multi-valued predicates. 0.30 Handles multi-valued 
predicates. Added include parameter to add predicate values to source.  Useful to short hand inference paths
* **2015-01-31** 0.31 Data structure enhanced to record type of intermediate object in paths.  Added recursive scaffolding for paths.  Added photo test case to extension.txt. 0.32 Use rdflib to generate triples 
from fuseki. Remove temp file processing for loading og graph -- load directly.  Refactor get_triples removing local functions to create serialized triples -- use rdflib instead. Remove "org" and "organization" references from the code.  Everything will be generalized.
* **2015-02-02** 0.33 update_def contains entity and column defs.  update_def is global.  Graph query generated from update_def -- local org references removed. Begin work on generating query for spreadsheet.  do_get output uses update_def, no hard coded column names.  do_get now uses a machine generated query.
* **2015-02-03** 0.34 general enumeration handling for get and update.  enum values in UPDATE_DEF are used to find files with enum tables.  The tables are loaded and used by do_get and do_update.  No hard coding remains.
* **2015-02-04** 0.35 Refactor do_get to simplify processing.  Values are now sets, either single or multi-valued. Begin work on multi-path update.  Two step path is working.  More testing required.  ENUM as global name.
* **2015-02-05** 0.36 Read and write the update definition as a JSON file.  Add pylint config to the project.  Address pylint messages. Add lint.txt report.  Add json file for update definition to the project.  Add vivfoundation to the project.  Eventually we will trim down vivofoundation to include only functions useful to the "pump".  Start calling this thing the VIVO data pump.  New files:
    * .pylintrc -- a pylint config for this project
    * lint.txt -- pylint output for sv_orgs.py
    * update_def.json -- the JSON representation of the update definitions
    * update_def_frag.py -- Python code for the JSON definitions. _DEPRECATED_
    * vivofoundation.py -- Support code for the pump.  Will be renamed.