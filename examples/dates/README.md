# Add Dates to VIVO

VIVO can treat dates as first class entities.  The example here puts dates in VIVO.  There are three cases:

1. Year precision dates.  These are dates where only the year is specified.  
1. Year Month precision dates.  dates where the month and year are specified.  In common use for publications.
1. Year month day precision dates.  The common yyyy-mm-dd form where all three elements of the date are specified.
  
*Note: VIVO also supports year month day hour and year month day hour minute precisions, but these are datetimes, not
dates and are not supported by this example.* 

## Method

A small python program, `gen_dates.py` is distributed with this example to generate date data.  As delivered, it 
generates all dates from 1800-01-01 to 2050-12-31, 94,939 dates in all.  That may be too many or not enough for
your VIVO.  You can easily edit and rerun gen_dates to produce a different range of dates, or edit the resulting
data file dates.txt to include dates of interest for your VIVO.

You do not need to run `gen_dates.py` if the data in dates.txt is appropriate for your VIVO.

## Filters

No filters are used in this example.  dates.txt is ready to be used.

## Columns

The date file has three columns:

1. uri
1. Precision -- an indicator of the precision.  "y" indicates year precision, "ym" indicates year month precision.
1. Date -- the date value to be added to VIVO

## Enumerations

One enumeration is used:

1. `datetime_precision_enum.txt` -- given a code of 'y', 'ym' or 'ymd', returns the VIVO precision

## Running the example

1. Update the sv.cfg file to provide VIVO SPARQL API parameters for your site.  Your system administrator will know the 
values of these parameters.
1. Run Simple VIVO to produce the date_add.rdf and date_sub.rdf.  Parameters are supplied by the `sv.cfg` file.

    python sv.py