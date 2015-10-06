Positions have five attributes:

1. Start date -- from an enumeration of dates of the form yyyy-mm-dd
1. End Date -- from an enumeration of dates of the form yyyy-mm-dd
1. Organization of Position -- from an enumeration of organizations by name
1. Person in position -- from an enumeration of people by orcid
1. Job title -- open text

## The steps to manage positions

1. Update your enumerations using `python make_enum.py`
1. Get positions from your VIVO using `python sv.py -a get`
1. Edit your spreadsheet `positions.txt` correcting and adding information for existing positions,
and adding new positions.  Use a text editor or spreadsheet program
1. Update the position information in your VIVO using `python sv.py -a update`

Repeat the steps as necessary.  