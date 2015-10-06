The Simple VIVO configuration (config) file tells Simple VIVO about your VIVO, what you would like to have done, and 
how you would like to do it.  Simple VIVO command line parameters override the values in the config file.  In this way, the config file can say what you usually do, and the command line can say what you would like done in this 
particular run.

For example, if you have a config file that tells Simple VIVO everything it needs to know to update the people in
your VIVO, you can run Simple VIVO using

```
python sv.py
```

No parameters are needed.  But if you would like to see all the internal messages that Simple VIVO generates while it is working, you can use:

```
python sv.py -v
```

You can get a complete list of all the command line parameters by using

```
python sv.py -h
```

By default, Simple VIVO expects your config file to be named `sv.cfg`.  But you can call it whatever you would like and tell Simple VIVO the name of your config file on the command line.  

For example, suppose you name your config file 'uf_production_sv.cfg`, which might be a good name if you are at the University of Florid and your config file is describing the production environment.  You would run Simple VIVO using:

```
python sv.py -c uf_production_sv.cfg
```

# Config file parameters

A sample config file `sv.cfg` is shown below.  

## Sections

Sections have names of the form `[sectionname]`  There are three section headers in the config file.  They can appear in any order.

``[sparql]``  specifies parameters to be used to access your VIVO.  

``[pump]`` specifies parameters to be used to perform Pump operations.

    [sparql]
    queryuri = http://localhost:8080/vivo/api/sparqlQuery
    username = vivo_root@school.edu
    password = v;bisons
    prefix =
        PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl:   <http://www.w3.org/2002/07/owl#>
        PREFIX vitro: <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
        PREFIX bibo: <http://purl.org/ontology/bibo/>
        PREFIX event: <http://purl.org/NET/c4dm/event.owl#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX obo: <http://purl.obolibrary.org/obo/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX uf: <http://vivo.school.edu/ontology/uf-extension#>
        PREFIX vitrop: <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
    [pump]
    action = get
    verbose = false
    inter = tab
    intra = ;
    nofilters = false
    defn = position_def.json
    src = position_update_data.txt
    uriprefix = http://vivo.school.edu/individual/n

## Parameters

Parameters take the form `name = value`.  All parameters are optional.  Parameters must appear in the appropriate section.  Within the section, the parameters may appear in any order.  The parameters that may appear in each section are defined below.

Section | Possible parameters
--------|--------------------
sparql  | queryuri, username, password, prefix
pump    | action, verbose, inter, intra, nofilters, defn, src, uriprefix

Each is described below.

`queryuri` gives the URI of the SPARQL API interface to your VIVO.  That is, the URI that will be used to make queries to your VIVO.  This URI is new in VIVO 1.6.  The Pump requires VIVO 1.6 or later.  The sample value is for a VIVO Vagrant, a test instance.

`username`  gives the username (VIVO may call this "email") for an account that is authorized on your VIVO to execute the VIVO SPARQL API.

`password`  gives the password of the account that is authorized on your VIVO to execute the VIVO SPARQL API.  That is, the password to the account specified by the `username`

`prefix`  gives the SPARQL prefix for your VIVO.  SPARQL queries typically use PREFIX statements to simplify the specification of URI in SPARQL statements.  The value of the prefix parameter should be the collection of PREFIX statements used at your VIVO.  Note that formatting of the parameter -- each PREFIX statement begins on a new line, including the first one.  Each is indented by four spaces.  This is recommended.

Note: All parameters are optional.  If a parameter is not specified, the Pump software will supply a default value.  But the default values for the Pump software are set for a VIVO Vagrant, not your VIVO.  You should consider the four parameters above to be required for your `sv.cfg`.
 
`action` is the desired Pump action.  There are four choices:  update, get, summarize and serialize.  Often these are specified on the command line to override the value in the config file and make explicit what action Simple VIVO is performing.

`verbose` is set to `true` to have the Pump produce output regarding the status and progress of its actions.  The default is `false` which produces limited output showing the the datetime the action started, the number of entities effected, and the datetime the action was completed.

`inter` is the inter field separator character used for your spreadsheets.  a CSV file would have `inter = ,`, a tab separated spreadsheet (recommended) would have `inter = tab`.  Note the word "tab".  the Simple VIVO config file uses this to specify a tab as a field separator.  Another popular choice for field separator is the "pipe" character "|".  Pipe and tab are used as separators because these characters do not appear in literal values in VIVO.

`intra` is the intra field separator character used to separate multiple values in a single spreadsheet cell.  The default is a semicolumn.

`nofilters`  set to `true` indicates that filters specified in the definition file should not be used.  Set to `false` indicates filters are to be used as normal.

`defn`  specifies the name of the file that contains the definition file, in JSON format, to be used by Simple VIVO.

`src`  specifies the name of the input source file (for update) or output file (for get).

`uriprefix`  indicates the format of any URI to be created by the update process.  URI will have random digits following the prefix.  So, for example, if your prefix is `http://vivo.school.edu/n`, Simple VIVO will create 
new entities with URI that look like `http://vivo.school.edu/nxxxxxxxx` where `xxxxxxxx` are random digits.