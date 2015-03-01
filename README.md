# The VIVO Pump

A general tool set for managing data in VIVO using data rectangles (rows and columns)

The Pump uses a definition file in JSON format that describes the nature of the rows -- entities in VIVO -- and the 
relationship of the columns to the graph of data in VIVO.  Each row/column intersection is an "instruction" to the Pump:

* blank or empty means do nothing
* None means remove any value found in VIVO
* a value means replace the value in VIVO with the value in the rectangle.

The Pump has two major operators:

1. Get -- gets values from VIVO according to the definition and returns a rectangle
1. Update -- uses a rectangle and updates VIVO according to the definition
    
A command line tool using the pump (Simple VIVO) is delivered with the pump.  Simple VIVO support data management of
VIVO data from a "spreadsheet" -- a delimited file of rows and columns, and a corresponding definition file.  Simple
VIVO supports get and update, along with some reporting operators.  For example:

    sv get org_def.json orgs.txt
    
will use the definition file org_def.json to get data from VIVO and return it in orgs.txt

    sv update person_def.json people.txt
    
will use the definition file person_def.json and the data people.txt to make updates in VIVO