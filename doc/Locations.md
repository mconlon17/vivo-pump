VIVO can store information about locations such as cities, buildings, and campuses.  One Simple VIVO definition can
be used to manage all your locations, or you may choose to use source files specific to different kinds of locations -- 
one for cities, one for buildings, one for campuses.

Many types of things are locations.  The most common are campuses, buildings, countries, and cities, but see the file `examples\locations\location_types.txt` for a complete list of VIVO location types.

Regardless of the type of location, each location has:

1. a name
1. one or more types such as building, campus, country or city
1. within -- an indication that one location is within another.  For example, a city is within a country, a building is 
within a campus.
1. latitude.  Negative is south.
1. longitude.  Negative is west.

We can use one Simple VIVO scenario to manage all of our locations.

1. See `locations.txt` for sample locations.  
1. Using a spreadsheet, edit this file to remove locations that you do not wish to have in your VIVO.
1. Add locations of interest for your VIVO.
1. Run 
    python sv.py -a update
   to put locations in your VIVO.
1. Use
    python sv.py -a get
   to get a spreadsheet of all the locations currently in your VIVO.
   
That's it.

Two additional examples are provided.  Buildings can be managed using the methods described below.  You may find
that having buildings in their own spreadsheet makes working with them easier than having all your locations in
a single spreadsheet.

A second example provides a data set of United States cities with populations of over 100,000.  This data set can be
loaded into your VIVO and used to provide references for events and other VIVO entities that reference
locations.


## Manage Campus Buildings using Simple VIVO

Buildings are locations.  Each has a name, a URL (may point to an enterprise system, an existing university web page 
about the building, historical information, or any other information resource about the building), a latitude and
longitude.

### Note

A sample file of buildings at the University of Florida is provided in uf_buildings.txt

### How to use

1. Use the sv_buildings.cfg config file to get your buildings from VIVO, as in:
    python sv.py -c sv_buildings.cfg -a get
1. Edit the resulting buildings.txt file to add your buildings
1. Update VIVO using
    python sv.py -c sv_buildings.cfg -a update
1. Add the resulting RDF to VIVO


## Add US Cities to VIVO

Add cities in the United States with population over 100,000 in 2015 to VIVO.  List came from Wikipedia,updated with
cities over 100,000 in Puerto Rico.

Each city has a name, a state, latitude and longitude.

Look up the state in VIVO through an enum.  If not found, throw an error -- all the states need to be in VIVO.  VIVO
is missing District of Columbia and Puerto Rico.  These need to be added by hand before the cities can be added.

Look up the city in VIVO.  Update the state, lat and long as needed.

### Note

There's nothing US specific about this code.  The data file contains US cities.  Edit the data file
to add cities of interest in provinces or states of interest.

The def file assumes that the wgs ontology has been added into
your VIVO.  See [World Geodetic System](https://en.wikipedia.org/wiki/World_Geodetic_System) in Wikipedia 
and [Basic Geo Vocabulary](http://www.w3.org/2003/01/geo/) and 
the  [RDF file](http://www.w3.org/2003/01/geo/wgs84_pos#)

### How to use

1. Add District of Columbia to your VIVO as a State or Province.  Add to state_enum.txt
1. Add Puerto Rico to your VIVO as a State of Province.  Add to state_enum.txt
1. Add the cities to your VIVO using an sv update as shown below:
    python sv.py -c sv_cities.cfg -s us_cities.txt -a update
1. Add the resulting RDF to VIVO
1. To see your city data and manage it in the future, you can do an sv get
    python sv.py -c sv_cities.cfg -a get
