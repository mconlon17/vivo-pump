# UF Grants Ingest

The UF Division of Sponsored Programs provides data to VIVO each week.  DSP data is queried and shaped into a CSV for
use by VIVO.  The file has multi-valued fields containing lists of principal investigators, co-principal investigators,
and investigators, all keyed by ufid (see Person Ingest).

Each record corresponds to a single award.  All awards since 2007 are processed each week and updated as needed.  Award
amounts, titles and participant lists change and are updated by the ingests as needed.

Each award has a sponsor.  Sponsors are keyed by a localSponsorID.  This identifier is stored in VIVO.  A separate
sponsor ingest updates the sponsors and is run prior to the grant ingest.

Each award has an administering department keyed by UF local deptid.  

When the ingest can not find the corresponding entity to which it should be linked (administering department,
investigator, sponsor), error messages are produced in the log.  The award is entered with no link to the unfound
entity.  Data managers should provide the missing entities based on the log reports, or correct the grant data to 
indicate correct linkages.  Subsequent ingests will then provide linkages.

## Filters

TBA

## Handlers

None anticipated

## Process

1. Obtain a current grants.csv file from DSP
1. Run the filters to produce the required input file
1. Run the pump to create add and sub RDF
1. Inspect the log for linkage errors.  Correct if possible.  Rerun pump if needed.
1. Add the add RDF and subtract the sub RDF
1. Update appropriate documentation regarding actions and results