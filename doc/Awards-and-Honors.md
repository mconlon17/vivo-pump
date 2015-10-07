To add awards and honors to VIVO, we need to know several pieces of information for each award or honor:

1. Who got the award or honor?
1. What award or honor was received?
1. From what institution?
1. What is the date of the award?

## Managing Enumerations

Each is represented by an enumeration:

1. person_enum for who
1. award_enum for what
1. org_enum for where
1. date_enum for when

The python program `make_enum.py` can be used to update these enumerations using data from your VIVO.  To run 
`make_enum.py` use:

    python make_enum.py
    
## Managing Awards

You can use 

    python sv.py -a get
    
to get the awards from your VIVO into a spreadsheet called `awards.txt`  You can add awards to your spreadsheet being sure to use values from each of your enumerations.

Once you have awards to add to VIVO, run:

    python sv.py -a update
    
which will create the `award_add.rdf` and `award_sub.rdf` to update your VIVO.

## Adding People, Dates, Awards and Organizations to your VIVO

To manage awards, your enumerations must be up to date.  Each award, person, organization, and date must already be in  your VIVO and in your enumerations.  Updating your enumerations is simple -- run `make_enum.py` as shown above.

If you need to add dates, rerun the dates example with a wider date range.

To add a single person, name of an award or an organization conferring an award, use the VIVO web interface.  Update
the enumerations, add a row to your awards.txt for the new award and run a Simple VIVO update.  

For example:

John Smith earns a lifetime achievement award from the American Cancer Society in 2015.  John Smith and the date 2015 are already in your VIVO, but the American Cancer Society and the lifetime achievement award are not.

1. Use the Site Admin interface to add the American Cancer Society as an organization.

1. Use the Site Admin interface to add "ACS Lifetime Achievement Award" as an award.

1. Update the enumerations.  Now all four elements of the award receipt are in your VIVO and you can add a row to your awards.txt spreadsheet that looks like

    `John Smith  ACS Lifetime Achievement Award  American Cancer Society 2015`
    
1. Run

    `python ../../sv.py -a update``
    
and the award will be in place.



