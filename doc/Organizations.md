You will want to have organizations in your VIVO for a number of reasons:

1. Organizations are the units of your institution -- your colleges, academic departments, administrative
units, and laboratories.  By representing your organization and its structure (which organizations are parts of others) you will be able to produce reports and visualizations based on your organizational structure, and answer questions such as number of faculty per organization, number of mentors, expertise at the organizational level, productivity and other other assessments.
1. Organizations are where your people had positions prior to being at your institution.
1. Organizations are where your people were educated.
1. Organizations provided grant funding to your organization.
1. Organizations where your faculty have collaborators that they work with on scholarship.
1. Organizations are employers of your graduates.

To put organizations in VIVO, you will want to have a spreadsheet of the organizations that you can use to manage the organizational data.  As organizations come and go, add and remove them from your spreadsheet.  As more information about organizations becomes available, or as organizational information changes (contact information, web pages, etc), make the updates in your spreadsheet.  Use Simple VIVO to update VIVO using the values in your spreadsheet (see below).

Simple VIVO always allows three things to appear in a cell in a spreadsheet containing attributes for an organization:

1.  The value of the attribute.  See below.  The cell contains a name, or a phone number, or a zip code.
1.  The word None.  When None appears are the value of an attribute, Simple VIVO is directed to remove whatever attribute value it finds in VIVO.  For examples, see [[Simple VIVO|]]
1.  An empty cell, that is, nothing is in the cell. When Simple VIVO sees nothing in the cell, it does nothing -- it neither adds nor subtracts a value.  If your spreadsheet is mostly empty, it tells VIVO to mostly do nothing.  

Only filled cells are acted upon.  Cells with values are checked against VIVO.  If the value in the cell is different than the value in VIVO, the value in VIVO is replaced with the value in the cell.  If the value in the cell is the same as the value in VIVO, nothing is done. Cells withe the word None act to erase values from VIVO.  Whatever value is found in VIVO is removed, and no new value is provided.

# examples/orgs

[examples/orgs](https://github.com/mconlon17/vivo-pump/tree/master/examples/orgs) contains the files you need to manage organizations using Simple VIVO.

Your spreadsheet data will have the columns shown in the table below.  If you need more or fewer columns, your VIVO site administrator should be able to help you modify the `org_def.json` file distributed with Simple VIVO to provide the organizational attributes you need.

Column name  | Purpose
-------|-------
uri | The VIVO uri of the organization.  VIVO assigns a uri to every organization in VIVO.
remove | Used to remove organizations from your VIVO.
name | The name of the organization precisely as it will appear in VIVO
home_page | the URL of the home page of the organization
email | The email address of the organization
phone | The phone number of the organization
within | The name of another organization which is the parent of this one
address1 | Address line 1 for the organization
address2 | Address line 2 for the organization
city | The name of the city of the organization
state | The name of the state of the organization
zip | the sip code (postal code) of the organization
abbreviation | An abbreviation for the organization.  "NIH" for the National Institutes of Health, for example
overview | A paragraph of text regarding the organization
type| The organization's types.  See below.  Many organizations have multiple types.
successor | The name of the successor to the organization if it no longer exists

## Creating `org_enum.txt`

Run `make_enum.py` using:

    python make_enum.py

## Updating org values in VIVO

1. Get your orgs from vivo using `python sv.py -a get`
1. Edit `orgs.txt` using a text editor or a spreadsheet.  The file is delimited using the inter field delimiter, which defaults to the tab character.
1. Update your orgs using ``python sv.py -a update`
1. Add `org_add.rdf` to VIVO using the Site Admin Load RDF feature
1. Remove `org_sub.rdf` from VIVO using the Site Admin Remove RDF feature
1. Update the enumeration using `python make_enum.py`
1. Repeat these steps to make changes to your organizational data


## Adding orgs to VIVO

Adding orgs is simple -- just edit your spreadsheet to add a row.  Put as much data about the organization as you
have on the row in the appropriate columns.  Leave the rest of the columns blank.  In particular, leave the `uri` column blank.  Simple VIVO will assign a uri to your organization when it is added.

Follow the rest of the steps described for updating yourorg values.  Adds and updates can be combined in the same spreadsheet.

## Removing orgs from VIVO

Removing orgs is also very simple -- just edit your spreadsheet and put the word "remove" in the `action` column.
Each organization that has `remove` in the action column will be removed from VIVO.

## Maintaining subsets of orgs

You may find that you would like to have different kinds of organizations in different spreadsheets to simplify data management.  For example, you may wish to have your internal organizations in one spreadsheet and external organizations in another.  

To maintain subsets, follow the steps below:

1.  Create appropriate folders for your work.  You may want to manage the two collections from two different folders.
1. Copy the def file into each folder
1. Modify the def file to select the orgs of interest.
1. Copy the sv.cfg file into each folder
1. Modify the sv.cfg file to use the name of the definition file for your subset.  Modify the rdfprefix and source file name as appropriate to help you manage the subset.
1. Run your gets and updates as above in each folder for each subset.

# Future

We expect to be able to manage photos of organizations in the future.  Check back here to see if Simple VIVO supports photos.
