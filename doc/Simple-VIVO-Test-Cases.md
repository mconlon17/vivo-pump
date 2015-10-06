Simple VIVO is a command line interface to the Pump.

# Command Line Tests

Function  | Verbose | Def    |  Spreadsheet | Example
----------|---------|--------|--------------|--------
get       |    Yes  |  None  |   None       | sv -v 
get       |    Yes  |  None  |   Good       | sv
get       |    Yes  |  None  |   Poor       | sv
get       |    Yes  |  Good  |   None       | sv
get       |    Yes  |  Good  |   Good       | sv
get       |    Yes  |  Good  |   Poor       | sv
get       |    Yes  |  Poor  |   None       | sv
get       |    Yes  |  Poor  |   Good       | sv
get       |    Yes  |  Poor  |   Poor       | sv
get       |    No   |  None  |   None       | sv
get       |    No   |  None  |   Good       | sv
get       |    No   |  None  |   Poor       | sv
get       |    No   |  Good  |   None       | sv
get       |    No   |  Good  |   Good       | sv
get       |    No   |  Good  |   Poor       | sv get building_def.json bar
get       |    No   |  Poor  |   None       | sv get foo
get       |    No   |  Poor  |   Good       | sv get foo buildings.txt
get       |    No   |  Poor  |   Poor       | sv get foo bar
update    |    Same |  Same  |   Same       | Same 18 cases
summarize |    Same |  Same  |   Same       | Same 18 cases
serialize |    Same |  Same  |   Same       | Same 18 cases