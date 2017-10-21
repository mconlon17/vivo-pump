# Managing Organizations in VIVO using Simple VIVO

This example shows how to retrieve organizational data from VIVO and put it in a spreadsheet.  The spreadsheet 
can be edited to add new organizations, improve the data of organizations, and to remove or merge organizations.

To get organizational data from VIVO, modify your `sv.cfg` file to provide the query parameters for your institution.  
Your system administrator should be able to assist you with these parameters.  Then run:

    python make_enum.py
    
This will make an enumeration of all the organizations in your VIVO and their URI.  The enumeration is used to support
referring to parent organizations and successor organizations by their names rather than their URI.

Then run:

    python sv.py -a get
    
This will produce a spreadsheet call `orgs.txt`. Edit the tab-delimited spreadsheet as needed to improve the data 
regarding the organizations in your VIVO.

To update VIVO with your improved data, use:

    python sv.py -a update
    
The result will be `orgs_add.nt` and `orgs_sub.nt` data.  These should be added to VIVO and subtracted from VIVO 
respectively, using the VIVO Site Admin menu.

Repeat the steps here, starting with `make_enum.py` to continue to improve your organizational data.
