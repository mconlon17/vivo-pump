# UF Pump Examples

These examples show actual configurations used at the University of Florida to maintain VIVO.

They may require UF ontology extensions.

## Organizations

UF updates organizations as needed.  UF organizations are classified as UFEntity.  UF organizations are identified
using deptid, an 8 digit number with positional logic.  Each department may have more than one deptid since 1) not
all deptids represent organizations, some represent managed entities or buckets of money, and 2) UF VIVO does not
attempt to represent all organizational detail at UF.  Student organizations (more than 800) are not represented unless
someone refers to the organization on their profile.  All colleges, departments, centers and institutes are represented.

## People

UF adds people to its VIVO each week, based on a feed of position data from HR.  UF employees are identified by UFID,
a single, opaque, random, eight digit number.  Professional staff, faculty, postdocs, consultants and others are added.  
Students are not added unless they ask to be added.  Graduate students are not currently added, but would be added with
a simple change in the pump scripts.  People are marked UFCurrentEntity if they appear in the position file for the 
week. 

## Positions

UF updates positions for people each week.  Positions are linked to people by UFID, and to UF organizations by
deptid (see above).  Data from the university enterprise data warehouse is extracted and used to update both people
and positions.  Some positions disclose sensitive information and are not entered by rule.  UF uses positions for
some non employment purposes and these records are filtered and not added to VIVO.

## Grants

Grant award data are added to VIVO each week from files created from Division of Sponsored Programs data resources. All
grants are reviewed and updated each week.  Titles, award amounts and investigator lists (PI list, Co-Inv list,
Investigator list) are updated as necessary.  UF does not record total award amounts -- only amount received.  This
means that award amounts in VIVO may start at zero and be updated as funds are made available by the sponsor.

Coming soon

## Publications

Publications are entered from BibTex files produced from Thomson Reuters Web of Knowledge.  The BibTex file is produced
each week.  Disambiguation algorithms attempt to match the name of each UF author to UF people in VIVO.  When unique
match cn not be achieved, reports are produced for manual review and finishing.  If the paper is indexed in PubMed,
PubMed is accessed and MeSH terms, abstract and link to on-line version are added to the paper's representation in
VIVO.

Coming soon

## Courses

Teaching data from the Office of the University Registrar is used to maintain a list of courses and data regarding
the teaching of those courses via "course sections."  VIVO does not currently recognize the course concept, only
the course section concept -- the teaching of a course.  See below regarding Course Sections.  A UF extension
to VIVO-ISF includes ufc:Course -- the abstract entity which participates in course catalogues and prerequisites.
 
Course data is updated 4-6 months after each term.  The data provided by the OUR is replicated and used to load
both courses and course data.

## Course Sections

Course sections (VIVO calls these courses) are instances of courses.  Course sections have a term, an instructor and
and relate to a specific course.  Course sections have section numbers.  Courses have course numbers such as Economics
101.

Course section data is updated 4-6 months after each term.

Coming soon.

 

