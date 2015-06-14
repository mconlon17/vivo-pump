# Add US Cities to VIVO

Add cities in the United States with population over 100,000 in 2012 to VIVO.

Each city has a name, a state, altitude and longitude.

Look up the state in VIVO through an enum.  If not found, throw an error -- all the states need to be in VIVO.

Look up the city in VIVO.  Update the state, lat and long as needed.

## Note

There's nothing US specific about this code.  The data file contains US cities.  Edit the data file
to add cities of interest in provinces or states of interest.

The def file assumes that the wgs ontology has been loaded into
your VIVO.  See [World Geodetic System](https://en.wikipedia.org/wiki/World_Geodetic_System) in Wikipedia and [Basic Geo Vocabulary](http://www.w3.org/2003/01/geo/) and the  [RDF file](http://www.w3.org/2003/01/geo/wgs84_pos#)

## To Do

1. Create a states_enum.txt for getting states.
1. Write cities_def.son for round tripping the data using the pump.
1. Add the code and data to Simple VIVO as one of the delivered data packages.
