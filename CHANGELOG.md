
# Changelog for the pump

* **2015-01-20** Code frame and to do list
* **2015-01-21** argparse for command line, read tab-delimited text file from args, first output tab delimited file 
from VIVO
* **2015-01-22** get is complete
* **2015-01-27** General data structure for updates and updates.  Now handles datatype and lang.  Handles updates 
and adds. Handles all six value conditions.
* **2015-01-29** Enumerations handled.  Filters handled.
* **2015-01-30** 0.29 Data structure enhanced to indicate multi-valued predicates. 0.30 Handles multi-valued 
predicates. Added include parameter to add predicate values to source.  Useful to short hand inference paths
* **2015-01-31** 0.31 Data structure enhanced to record type of intermediate object in paths.  Added recursive 
scaffolding for paths.  Added photo test case to extension.txt. 0.32 Use rdflib to generate triples 
from fuseki. Remove temp file processing for loading og graph -- load directly.  Refactor get_triples removing local 
functions to create serialized triples -- use rdflib instead. Remove "org" and "organization" references from the code.  
Everything will be generalized.
* **2015-02-02** 0.33 update_def contains entity and column defs.  update_def is global.  Graph query generated from 
update_def -- local org references removed. Begin work on generating query for spreadsheet.  do_get output uses 
update_def, no hard coded column names.  do_get now uses a machine generated query.
* **2015-02-03** 0.34 general enumeration handling for get and update.  enum values in UPDATE_DEF are used to find 
files with enum tables.  The tables are loaded and used by do_get and do_update.  No hard coding remains.
* **2015-02-04** 0.35 Refactor do_get to simplify processing.  Values are now sets, either single or multi-valued. 
Begin work on multi-path update.  Two step path is working.  More testing required.  ENUM as global name.
* **2015-02-05** 0.36 Read and write the update definition as a JSON file.  Add pylint config to the project.  Address 
pylint messages. Add lint.txt report.  Add json file for update definition to the project.  Add vivofoundation to the 
project.  Eventually we will trim down vivofoundation to include only functions useful to the "pump".  Start calling 
this thing the VIVO data pump.  New files:
    * .pylintrc -- a pylint config for this project
    * lint.txt -- pylint output for sv_orgs.py
    * update_def.json -- the JSON representation of the update definitions
    * update_def_frag.py -- Python code for the JSON definitions. _DEPRECATED_
    * vivofoundation.py -- Support code for the pump.  Will be renamed.
* **2015-02-06** 0.37 Minor code improvements to address pylint and pyCharm suggestions
* **2015-02-06** 0.38 WORK IN PROGRESS.  New vivopump library.  New calls.  Updating code.  0.38 is not operational.
* **2015-02-06** 0.39 pyunit tests for each function in vivopump.  Tests pass.  More tests can/should be added.  
sv_orgs operational.  get and update tested.  Code now refers to vivopump for helper functions and uses new vivopump 
function names. prepare_column_values split out from do_get.  Added label and type triples for intermediate objects
* **2015-02-07** 0.40 Refactor main code for clean pylint and clean pycharm.  Two step path testing looks good
* **2015-02-08** 0.41 Draft grant_def.json for grant management in VIVO.  Requires three new enums (deptid, sponsorid, 
ufid), and five new filters (datetime, title, dollar_amount, deptid, sponsor_award_id).  Added improve_title, 
improve_dollar_amount, and comma_space to vivopump.  Test cases for each added to test_vivopump
* **2015-02-09** Date, deptid and sponsor award id filters added to vivopump.py.  Tests added to test_vivopump.py.  All 
enumerations added.
* **2015-02-10** Improve formatting of get query. Improve comments. Update for buildings as test case.
* **2015-02-11** 0.42 Improve make_get_query to avoid nested optionals.  Handle value in VIVO not in enumeration table. 
Improve def files.  Now have person, section, pub, grant and building.  All run in Jena, but not all run in Fuseki.
* **2015-02-14** 0.43 -v option for verbose output.  Move write_update_def to vivopump.  Add test case.
* **2015-02-15** 0.44 Using sparqlwrapper in new vivo_query.  Using stardog SPARQL endpoint.  Add pystardog to repo.  
Add try_sparqlwrapper to repo.
* **2015-02-16** 0.45 Warn regarding multiple values in VIVO for single valued predicate paths
* **2015-02-17** 0.46 Named pump.py.  Default files are pump_def.json and pump_data.txt.  Improved help. Unicode bug 
fixed in update.  Enum not found fixed in update.  Fixed bug in do_get regarding tabs in fields.
* **2015-02-18** Course_def.json and course_data.txt.  Can all the linkages be created by the pump? Begin framing the 
Pump class. Begin framing the unit tests for add, change and delete elements.  Restructure files and folders for unit 
tests and data.  See wiki for test cases.
* **2015-02-19** 0.47 Pump() is now a class in its own file pump.py.  sv (Simple Vivo) is a main program that runs the 
pump. Pump Serialize test case.
* **2015-02-20** Added test case descriptions for simple vivo as wiki page to the pump repo for command line testing
* **2015-02-21** Minor code formatting and comment improvements
* **2015-02-24** 0.48 Clean up the repo.  Removing unused files. Rewrote 2 of 3 step 2 cases, warnings that third are 
not finished.  **UNTESTED**
* **2015-02-25** 0.49 Preparing test frames for unit tests of data cases. Improve comments. Refactor update() and 
do_update() to support injection of data via JSON rather than file -- used for test cases. Lots of progress with 
refactored code, tracking down bugs and writing test cases for update().  do_update() now returns the add and sub 
graphs.  These are now tested directly in the test cases for appropriate triples in each test case.  First three 
data use case tests (see wiki) complete.
* **2015-02-26** 0.50 Two additional test cases coded and passed -- Add for unique two step path.  A test case for 
creating the path, and another for adding an attribute to an existing intermediate entity.  Refactor get_graph to use 
new make_update_query().
* **2015-02-27** 0.51 New make_update_query for path length 1 and path length 2 working as expected. Refactored 
get_graph to handle path length 2 and 3
* **2015-02-28** 0.52 make_update_query for path length 3.  Removed use of global variables UPDATE_DEF and ENUM.  No 
more globals! Begin moving support functions to the vivopump module.  make_update_query moved. Remove duplicated to dos
* **2015-03-01** 0.53 Move read_update_def, make_rdf_term, get_graph to vivopump.  Add test cases for each.  Fixed bug 
in make_update_query resulting from implicit casting of URIRef to string. Refactor make_update_query and get_graph to 
make slices of the graph and combine them, one slice per path in the update_def.  Much faster. Clean up test files.  
do_update() refactored to push two_step_update to its own function.  Additional two step test cases.  Test two step 
test cases pass.
* **2015-03-02** 0.54 Refactor update() to remove unused columns defs from the update def prior to get_graph.  
get_graph() runs in liner time based on number of columns.  Reducing the number of columns to the columns that are in 
common between update_def and update_data significantly speeds up the get_graph() and supports writing "large" 
update_defs.  Fixed bug in get_graph() -- now includes all entities as specified in the entity sparql.  _FIRST_ path 
length three test passed!
* **2015-03-03** Improved testing of path 3 partial path
* **2015-03-04** test_sv.py started for testing Simple VIVO command line scenarios
* **2015-03-05** Improve person_def.json to include research areas.  Add people_types.txt as a enum for types.  
faculty.txt is a spreadsheet of faculty resulting from an sv get
* **2015-03-06** Code formatting and to do improvements
* **2015-03-07** 0.55 Three new test cases for unique three length paths.  Add, Change, Delete working on three length 
unique paths.
* **2015-03-11** Four new test cases for multi-value one length path.  Add, change, change/no-op, Delete are working 
on multi-valued length one paths.
* **2015-03-15** 0.56 Can inject original graph to the pump.  Useful for testing.  Added test case using injected 
original graph
* **2015-03-21** 0.57 Enum values in update_def are now full path names to find filenames anywhere.  Root filenames 
become the names of the enums in the structures.
* **2015-03-25** Improved directory structure.  Examples folder now has subfolders for each domain -- buildings, 
faculty, orgs, etc
* **2015-03-30** 0.58 Remove feature added.  A column named "remove" may appear in the update spreadsheet.  If the 
value in the remove column is "True" or "true", then the pump will remove all triples related to the uri as either 
subject or object. To do now relate only to the software. Test case to dos are in test_vivopump.py.  Test cases added 
to test_vivopump.py.  *UNTESTED* Enhancement of examples are now issues in the GitHub repo -- if creating or working 
or testing these new examples results in desired software changes, these will be entered as appropriate to dos in the 
appropriate software file.
* **2015-04-01** Remove works as designed.  Perhaps not as expected.  It removes triples available to the update.  We 
might have thought it removed all triples associated with entity.
* **2015-04-06** 0.59 Add no filters option to command line in sv.  get -nf shows VIVO data "as is".  get shows data 
with filters as defined in update_def. do_get now works with our without filters.  Without filters you can see what 
VIVO has.  With filters you can get a spreadsheet ready for update.  Filters done before enumerations, so an improved 
value may be enumerated.  Filtering removed from update. File minimal.txt removed.  New test class for testing get 
scenarios.  Two new test cases for get -- with and without filters.  Added support for lang parameters.  If a literal 
has a lang attribute in the update_def, it will be used to add triples. Support for dataype has also been added, but 
additional work is needed.  So consider this *UNTESTED*
* **2015-04-07** 0.60 read_update_def recursion simplified.  cast_to_rdflib added to read_update_def to support rdflib 
datatypes.  data type test cases pass.  Order of columns in def file is now preserved in the update_def.  New test case 
for update_def order checking passes.  Order now used in get.
* **2015-04-09** Planned feature removed from the plan.  Had thought that the pump would support look-up by keys other 
than URI.  Now see no reason for this additional complexity.  When an update is performed with no URI, a URI is creat
and the row is added.  When get is run, URIs are fetched.  All is good.
* **2015-04-12** vivopump.py now supports use of the VIVO API for sparql query.
* **2015-04-18** 0.61 Null values in source data removed prior to update.  Fixed bug in enum filename.  uf_examples 
remove_current working as expected.  Work in progress on add_current
* **2015-04-19** Start work on ConfigParser for sv.py.  All options specified.  Too easy.
* **2015-04-22** Begin work on person ingest.  Too hard.  Without position_data.csv
* **2015-04-29** Work on make_person_update_data in uf_examples.
* **2015-05-01** Add salary plan enum to uf_examples
* **2015-05-02** Progress on make_person_update_data
* **2015-05-05** make_person_update_data now using contact shelve.  All cases working as expected.
* **2015-05-06** write_csv added to vivopump.  Test case added to test_vivopump.
* **2015-05-07** Now making UF Person Data from source
* **2015-05-08** Change approach in uf_examples to a chain of filters to get from uf source data to a pump update file
* **2015-05-09** Add all shelve files to uf_examples/person. Add read_csv_fp and write_csv_fp, and test cases, for 
reading and writing csv files from a file pointers rather than a filename.  Supports reading and writing from stdin 
and stdout. ufid_exception_filter added to uf_examples/person -- removes ufid on an exception list from the data to 
be processed by the pump. privacy_filter added to uf_examples/person.  Removes people from processing if they have 
privacy flags and/or can not be found in the UF privacy data.  That is, they must be found and must have privacy flags 
that allow them to be in VIVO.  Add get_vivo_ufid to vivopump.py and a test case to test_vivopump.  The function 
queries vivo and returns a dictionary keyed by ufid where items are uri.  merge_filter has been added to 
uf_examples/person.  The merge_filter combines data from UF with data already in VIVO to ensure updates of data already 
in VIVO as well as the addition of new people from source.
* **2015-05-10** merge_filter adds uri and current columns only.  No extraneous columns.  manage_columns_filter.py to 
add and remove columns added to uf_examples/person.  ufid_exception_filter now marks people as remove.  This will apply
not only to people in the source, but people in VIVO if the merge filter is run first.  contact_filter.py added to 
uf_examples/person to add contact data to the pump input file. uri_exception_filter.py added to uf_examples/person. Add
salary_plan_filter to uf_examples/person
* **2015-05-11** Add homedept_assignment_filter.py to uf_examples/person to handle privacy issues resulting from people
having home departments in restricted in departments.  update the manage_columns_filter to remove vars related to
positions.
* **2015-05-12** person_update_data.txt added to uf_examples/person. Clean-up unused files from uf_examples/person. 
Start work on uf_examples/person/person_def.json
* **2015-05-13** Start work on uf_examples/positions.  Three filters.
* **2015-05-14** merge_filter added to uf_examples/positions.
* **2015-05-15** Remove the current_people example from uf_examples.  This is now handled by uf_examples/person.
* **2015-05-16** Add improve_jobcode_description to vivopump.py and three test cases to test_vivopump.py.  Add 
position_exception_filter.py to uf_examples/positions to handle positions that do not qualify for VIVO.
* **2015-05-17** Add positions_def.json to uf_examples/positions.
* **2015-05-18** Additional work on position_def.json.  Check 1.8
* **2015-05-19** Add position enum -- ufid and deptid -- to uf_examples/positions
* **2015-05-21** Complete draft of positions_def.json in uf_examples/positions
* **2015-05-22** people_types.txt, improve person_update_data.txt, improved person_def.json added to uf_examples/person
* **2015-05-23** Add orgs to uf_examples
* **2015-05-24** Improve README and TO DO.  Improve uf_examples/position_def.json
* **2015-05-25** Support for courses.  See uf_examples/courses.  Three new filters -- manage_columns_filter, 
unique_ccn_filter, merge_filter.  One new vivopump function get_vivo_ccn for finding courses by common course number 
(UF primary key).  One new text improvement function -- improve_course_title for improving abbreviations in course 
titles.  New test cases for improve_course_title.  Course data, course_def.json, README added to uf_examples/courses.  
Filters work as expected.  Ready for upload test to VIVO.
* **2015-05-26** sv 0.4 all command line parameters are keyword.  No positional parameters.
* **2015-05-27** sv 0.5 Reconcile config and command line.  Set defaults via dict.
* **2015-05-28** sv 0.6 All arguments are now defaulted in the software, can be supplied via the cofig, which
overwrites software defaults, and finally on the command line which overwrites both.  Each argument can be set in
any of these three ways.  Six arguments are currently implemented.  Six arguments to be implemented.
* **2015-05-29** args inter and intra are fed through the pump to get and update to read_csv and do_get
* **2015-05-30** Removed old_vivo_query from vivopump.py.  Replaced use of global variables with passed parameters.
new_uri() updated to use parms.  Test cases updated.  vivo_query() updated to use parms.  Test cases updated.  
query_parms passed through the pump.  uri_prefix passes through the pump.  All parms now passed to all consumers.
* **2015-06-01** Running sv on uf_examples/orgs. orgs_def to VIVO-ISF 1.6 (all but phone numbers)
* **2015-06-02** Investigating minor surgery needed to add a type assertion to the get query to isolate types of phone
numbers and create a unique path to value
* **2015-06-06** Support "qualifier", a new attribute in step definitions.  In some situations the path from the entity 
to the value may not be uniquely defined through a predicate path unless additional qualification is provided.
qualifiers are SPARQL statements which can be inserted to qualify any "object" in a path.  See 
uf_examples/orgs/org_def.json
* **2015-06-08** Repair calling sequences for do_two and do_three step updates. Remove extraneous prints.
* **2015-06-09** Minor update to org_def for testing.  Will need to use qualifiers in update to identify specific URI
* **2015-06-10** get_step_triples() used in update to get the triples corresponding to the current step.
* **2015-06-11** Some preliminary code in get_step_triples for qualifiers.  WIll need more triples in the update graph
to process qualifiers -- the update graph currently does not contain the triples needed to make the step queries.
* **2015-06-12** Start work on cities examples.  Data and README.
* **2015-06-13** Draft cities_def.json and states_enum.txt
* **2015-06-14** Dc and Pr added to cities data.  Generating RDF.
* **2015-06-15** cities.rdf looks good
* **2015-06-16** rdfprefix.  add and sub output files
* **2015-06-17** cities example is complete.  mycities.txt is the output of the get, demonstrating round tripping.
* **2015-06-18** More work on orgs
* **2015-06-22** Improve descriptions of course and course section in uf_examples
* **2015-06-23** New folders and README.md files now for all uf_examples to be created.  sections, sponsors,
grants, publications all still to come.
* **2015-06-24** Add raw code to uf_examples/sponsors.  Add sponsors.txt. manage_column_filters for sponsors
* **2015-06-25** Add Type assertions to uf_examples/org_def.json
* **2015-06-26** Refactor do_remove.  merge_filter for sponsors.  Sponsor_def.json improvements.  Add get_vivo_sponsorid
to vivopump.py.  sv.cfg for sponsors
* **2015-06-27** Sponsor example is complete.  add and sub rdf for UF sponsor data.
* **2015-06-28** Begin uf_examples/grants.  Data and json.
* **2015-06-29** Improve grant_def.json, add sv.cfg. Add qualifiers to make_update_query.  Begin to test various
qualifier scenarios.  Add qualifier to URL in orgs_def.json to select home page by label.  New get_step_triples with
qualifiers.  Passing first tests.
* **2015-06-30** Complete draft uf_examples/grants/grants_def.json
* **2015-07-01** Add enums to uf_examples/grants
* **2015-07-02** Add uf_examples/grants/vivo_grants.txt, the UF enterprise data for grants
* **2015-07-04** grants_add and grants_sub from runs on small_grants.  Need multi-step, multi-value update for 
investigators.
* **2015-07-05** Prep the uf_examples/publications area with recent code for pubmed ingest.  This code contains new
disambiguation code, Entrez fetch for pubMed, plus all mapping for pubmed to VIVO.  Expect to use this code as a
foundation for future ingest from DOI as well as ingest from PMID.
* **2015-07-06** Start uf_examples/publications/pub_def.json
* **2015-07-07** Additional publication prep
* **2015-07-08** Begin merging add_pubmed code
* **2015-07-10** bib2csv_filter, sample data in uf_examples/publications
* **2015-07-11** Refactored bib2csv using list comprehension.  Completed bib2csv_filter.  Working as designed. Add
tr_csv.txt as sample output from bib2csv.  Add publisher_column_filter.py. Add publisher_columns_filter.py. Add
publisher_update_data.txt.  Add unique_name_filter.txt. Add match_publishers_filter.py. Add publisher_def.json.
Add org_types to uf_examples/publications for adding publishers.  Add sv_publishers.cfg.  Add publisher_add.rdf and
publisher_sub.rdf.  Publisher work is complete in uf_examples/publications.  On to journals.
* **2015-07-12** Update uf_examples/README.md to document processes for journals. Add journal_columns_filter.py.  Add
journal_update_data.py. PEP-8 improvement to unique_ccn_filter.py. Add unique_issn_filter.py. 
Add match_journal_filter.py. Add sv_journal.cfg.  Add journal_def.json.  Add journal_add.rdf.  Add journal_sub.rdf.
On to concepts.
* **2015-07-13** Update uf_examples/publications/README.md to document the four ingests.  We do not ingest concepts
from TR as they are proprietary.  Add author_prep_filter.py.  Add author_update_data.txt.  Author name parts working.
Corresponding author working.  Still need to find UF authors.
* **2015-07-14** Add replace_initials to vivo_pump.  Add four test cases to test_vivo_pump.  author_prep_filter
identifies UF authors.
* **2015-07-15** Start on author_match_filter
* **2015-07-18** vivo_get_authors added to vivopump.py.  Test case added to test_vivopump.py.  Keys on display name.  
Needs something better.  Rename match filters to put entity first, match second.  Example journal_match_filter.py.
 author_match_filter.py runs as expected.  Needs better tests.
* **2015-07-19** improve_display_name added to vivo_pump.  Takes a display name strong and standardizes formatting. Used
in author_prep_filter.py.
* **2015-07-20** Add TODOs. Begin uf_examples/publications/author_def.json.  Add author_types.json
* **2015-07-21** Add sv_author.cfg
* **2015-07-26** Start pub_columns_filter.py.  Add pub_update_data.txt
* **2015-07-28** Add sv_pub.cfg.  Start pub_match_filter.py.  Improve uf_examples/publications/README.md
* **2015-07-29** Add parse_pages to vivopump.py with test cases in testvivopump.py. Update pub_columns_filter to 
create start_page and end_page in pub_update_data.txt
* **2015-07-30** Add parse_date_parts to vivopump.py and test cases in testvivopump.py.  Update pub_columns_filter to
create date in pub_update_data.txt
* **2015-08-24** Removed sparql.setCredentials from vivo_query.
* **2015-08-28** Finally! A complete, realistic, draft of the UF person_def.json  Whew.
* **2015-08-29** Improve README and copyright notices. Pylint and PEP code improvements for sv.py, pump.py and
vivopump.py
* **2015-08-30** Begin work in uf_examples/people to support person type update.  merge_filter, manage_columns,
salary_plan_filter updated.
* **2015-08-31** null_value_filter.py added to uf_examples/people.  The filter replaces values of "NULL" with values of 
empty string. Add deptid_enum.txt to uf_examples/people