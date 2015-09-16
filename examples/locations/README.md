# Managing Locations using Simple VIVO

VIVO can store information about locations such as cities, buildings, and campuses.  One Simple VIVO definition can
be used to manage all your locations, or you may choose to use source files specific to different kinds of locations -- 
one for cities, one for buildings, one for campuses.




# Add US Cities to VIVO

Add cities in the United States with population over 100,000 in 2015 to VIVO.  List came from Wikipedia,updated with
cities over 100,000 in Puerto Rico.

Each city has a name, a state, latitude and longitude.

Look up the state in VIVO through an enum.  If not found, throw an error -- all the states need to be in VIVO.  VIVO
is missing District of Columbia and Puerto Rico.  These need to be added by hand before the cities can be added.

Look up the city in VIVO.  Update the state, lat and long as needed.

## Note

There's nothing US specific about this code.  The data file contains US cities.  Edit the data file
to add cities of interest in provinces or states of interest.

The def file assumes that the wgs ontology has been loaded into
your VIVO.  See [World Geodetic System](https://en.wikipedia.org/wiki/World_Geodetic_System) in Wikipedia 
and [Basic Geo Vocabulary](http://www.w3.org/2003/01/geo/) and 
the  [RDF file](http://www.w3.org/2003/01/geo/wgs84_pos#)

# How to use

1. Add District of Columbia to your VIVO as a State or Province.  Add to state_enum.txt
1. Add Puerto Rico to your VIVO as a State of Province.  Add to state_enum.txt
1. Add the cities to your VIVO using an sv update as shown below:
    python ../../sv.py -v -a update -s cities.txt -r cities -d cities_def.json
1. Add the resulting RDF to VIVO
1. To see your city data and manage it in the future, you can do an sv get (optional):
        python ../../sv.py -v -a get -s mycities.txt  -d cities_def.json
