Dates in VIVO are just like other things in VIVO -- they have URI and they have attributes.  Unlike other things, however, VIVO creates the same dat many time, giving each its own URI.

Using Simple VIVO, we can create a set of dates for VIVO that are available for reuse in managing all other entities.

For example, when entering a publication in VIVO, one is asked to enter the date of the publication.  Rather than create a new date for each publication, we can create a set of dates that are reused for *all* publications.  This have several advantages over creating dates for each publication:

1.  It avoids semantic confusion.  Having two dates that represent the same thing (the same date) but have different URI is not a best practice.  We could assign "sameAs" predicates to equate all all the various entities representing the same date, but this just layers complexity on an unfortunate situation.
1.  It is simpler.  There is only one "December 18, 1993."  All things that need to refer to this date need to refer to the same entity in VIVO.
1.  It saves space.  As VIVO grows and adds publications, it adds dates.  But this is unnecessary.  There is a "slow growing" number of dates (one per day!)
1.  It supports look-up by date.  Rather than find all the entities with the same date value and then finding all the things associated with each of those values, we can find all things associated with the single entity that represents the date of interest.

# Date Precision

VIVO Supports the concept of "date precision."  This is a little unusual in the big world of data management, so let's take a look at what VIVO can represent.  VIVO provides three precisions for date values.  A date can be just a year, or just a year and a month (common in publication dating) or a year and a month and a day (common in most administrative function).  In some cases, systems other than VIVO are "required" by their internal formats to provide a day, month and year for all dates.  Many systems default the unknown components of the date to "1".  This means that when looking at a date (without a precision) of "1993-01-01" we are unable to discern whether the date value is informative about the month and day, or whether these are just place holders.  VIVO is capable of representing, with certainty, the level of precision in the date value.  The date value "1993-01-01" with a date precision of "<http://vivoweb.org/ontology/core#yearPrecision>" is the same as a date value of "1993" with the same year precision.  The month and day values are non-informative.

| VIVO date precision | Example| Since Jan 1, 1800  until Dec 31, 2050|
----------------------|--------|-------------------|
| <http://vivoweb.org/ontology/core#yearMonthDayPrecision> | "1993-12-18" |91,676 |
| <http://vivoweb.org/ontology/core#yearMonthPrecision>    | "1993-12"    | 3,012 |
| <http://vivoweb.org/ontology/core#yearPrecision>         | "1993"       | 251 |

# Pre-loading VIVO with dates

We can pre-load VIVO with dates using the dates example in Simple VIVO.  We can set a range of dates that will be useful for our VIVO, generate them and update our VIVO with them.  Subsequent updates can use the dates that are already in VIVO, rather than making more.

# examples/dates

The dates folder in examples has everything we need to pre-load our VIVO with dates.  

`gen_dates.py` is an optional Python program for generating a spreadsheet of dates data.  By default it generates dates from Jan 1, 1800 to Dec 31, 2050.  This should be more than enough for many VIVOs.  Dates are generated for each year, for each year/month combination and for each date in the range.  By modifying `gen_dates.py` it can produce dates in any range.

`dates.txt` is a tab delimited spreadsheet ready for the pump.

`sv.cfg` is a config file that defines the dates update.  You will need to edit this to supply query parameters for your site.  Your system administrator will be able to supply you with appropriate query parameters.

`date_def.json` is a definition file for putting dates in VIVO.  It defines three columns: 1) uri, 2) Precision, and 3) Date.

`datetime_precision_enum.txt` is an enumeration of the VIVO datetime precisions that allow the use of short codes "y", "ym" and "ymd" for the precisions described above.

To run the example, use:

```
python sv.py
```

The result will be two files: `date_add.rdf` and `date_sub.rdf`  Use the VIVO system administration interface to add `date_add.rdf` to your VIVO.  The result will be 94,939 dates.  You may never have to be concerned about dates again.

