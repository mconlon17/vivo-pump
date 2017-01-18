# Managing Memberships in Simple VIVO

Memberships have five attributes:

1. Start date -- from an enumeration of dates of the form yyyy-mm-dd
1. End Date -- from an enumeration of dates of the form yyyy-mm-dd
1. Group of Membership -- from an enumeration of groups (Committees, Associations, etc) by name
1. Person holding membership -- from an enumeration of people by label
1. memberships role -- open text.  Typically "Member" or "Chair"

## The steps to manage memberships

1. Update your enumerations using `python make_enum.py`
1. Get memberships from your VIVO using `python sv.py -a get`
1. Edit your spreadsheet `memberships.txt` correcting and adding information for existing memberships,
and adding new memberships, one row per membership.  Use a text editor or spreadsheet program
1. Update the membership information in your VIVO using `python sv.py -a update`

Repeat the steps as necessary.