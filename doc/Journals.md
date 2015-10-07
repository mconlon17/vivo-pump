# Managing Journals in Simple VIVO

Journals a re fundamental entity for VIVO.  To add publications to VIVO using Simple VIVO, the journals for the
publications must already be present in your VIVO.  You will want to load your VIVO with journal titles and add
journals as required for your publications.

## Adding journals to your VIVO

Simple VIVO provides a set of more than 6,600 academic journals, each with an ISSN.  Many also have an EISSN.

To add these journals to your VIVO, use:

    python -v -a update -s journal_data.txt
    
The result will be a two files:  `journal_add.rdf` and `journal_sub.rdf`  Use the VIVO System Admin interface to add 
the RDF in `journal_add.rdf` to your VIVO.  `journal_sb.rdf` should be empty.  If not, use the VIVO System Admin 
interface to subtract the RDF in `journal_sub.rdf` from your VIVO.

## Managing Journals in your VIVO

1. Use get to retrieve the journals from your VIVO to a spreadsheet

    `python sv.py -a get`
    
1. Edit your spreadsheet to improve your journal data, and add new grants.  You may need to remove duplicates, correct
spelling or otherwise improve the name of the journal, or add an EISSN if one is missing.

1. Use update to put your improved journal data back in VIVO

    `python sv.py -a update`
    
1. Repeat the steps each time you wish to improve your journal data