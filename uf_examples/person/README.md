# UF Person Ingest

Intended to be a weekly process to update information in VIVO about UF People.  Here's what's updated:

1. The population of people.  All UF business rules are followed regarding who should be in VIVO and how they 
should be represented.  Some rules (to be expanded)
    1. Qualifying type of person
    1. Does not have privacy flags that would prevent inclusion
1. The status of people -- UFCurrentEntity asserted if the person has a current relationship with VIVO.  The assertion 
is removed if the person is not associated with UF.  If the assertion is removed, contact information and preferred
title is also removed.
1. The contact information for people.  Includes their preferred title and UF Home Department (a UF extension).

In previous UF ingests, positions were handled in a single ingest along with people.  Now there is an ingest 
focused on people and a separate ingest focused on positions.