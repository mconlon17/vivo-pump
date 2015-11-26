# Managing Organizations in VIVO using Simple VIVO

This example shows how to retrieve organizational data from VIVO and put it in a spreadsheet.  The spreadsheet 
can be edited to add new organizations, improve the data of organizations, and to remove or merge organizations.

To get organizational data from VIVO, modify the `sv.cfg` to provide the query parameters for your institution.  Your
system administrator should be able to assist you with these parameters.  Then run:

    python sv.py -a get
    
This will produce a spreadsheet call `orgs.txt`. Edit that spreadsheet as needed to improve the data regarding the 
organizations in your VIVO.

To update VIVO with your improved data, use:

    python sv.py -a update
    
The result will be `orgs_add.rdf` and `orgs_sub.rdf` data.  These should be added to VIVO and subtracted from VIVO 
respectively, using the VIVO Site Admin menu.
