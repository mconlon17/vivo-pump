As we gain experience with Simple VIVO and the underlying Pump software, we'll collect ideas for future features here.  There are no promises here, and some ideas that seemed worthwhile at the time, may fade in importance as experience grows.

Some of the issues are for the "end user," which for Simple VIVO is typically the VIVO data manager.  Some are for programmers using the Pump.  And some are for the developers of the software to allow the software to grow and improve in a reasonable way.

Features are numbered simply to make referring to them easier.  The numbering does not imply an ordering.

*Note:  Some people may ask "why have future features in the wiki rather than in the issues?  After all, you can mark issues as "future" and exclude them from various lists.  And the answer is that I found that mixing the issues together was inconvenient and misleading.  GitHub does not have the ability to save queries of the issues, so each time I wanted to see the current issues, I had to explicitly exclude the issues marked "later".  Eventually I decided to gather the "later" features here and close them out of the issues list, reserving the issues list for features under active development.*

# Possible Future Features

1. Add an ontology diagram to each example to show what is going on.
1. Rename the "remove" column to "action" and provide remove as one of several actions.  Support a merge action
by providing a syntax to specify a mater and merge to the master. "a1" and "a" where "a" specifies a master and "a1" indicates "merge to a".  Could ten use any string as a mater identifier and any string with a number as merge to the master identifier.  Could specify many merges in one update.
1. Add SPARQL queries and visualizations to each example to reward data managers for getting their data into VIVO.
1. Add handler for photos. When a user specifies a photo filename as data, a handler should be available as part of the definition that can process the file, create a thumbnail, put the thumbnail and photo in appropriate places in the VIVO file system and generate the appropriate RDF.
1. Refactor two_step and three_step as recursive.  Pump should support any path length through recursive application of path. Need to be clever about "one back" and one forward" and then it should be feasible. Will take a good lucid morning.
1. Simple VIVO should read and write from stdin and stout respectively.  Support stdin and stdout as sources and sinks for source data.  As in: `filter | filter | python sv.py > file`
1. Simple VIVO should put data directly into VIVO with the need to write a file of RDF to be loaded manually.
1. Add support for auto-generated labels.  When adding awards and honors, the VIVO interface auto generates a label for the AwardReceipt.  Without that label, the award receipt displays its uri in the interface. When adding degrees, the VIVO interface does the same thing -- auto generates a label for the AwardedDegree.  We could just add a label field to each def and require the data manager to supply the label.  And a simple Excel function would auto generate labels in the spreadsheet. 
1. Support round tripping of the output of serialize.  The Pump serialize method was envisioned as a means of round tripping a text description of the state of the Pump for the purpose of restarting or recreating a Pump. To do this we will need:
    1. A complete description of the Pump state in serialize -- all instance variable values, update_def
    1. A means to define Pump via the output of serialize, as in `q = Pump.define(p.serialize())` should `define` Pump q to be the same as Pump p.
1. Add an example regarding human subject studies.  UF will allow its approved human subject studies to be posted in VIVO and associated with investigators.  This is a  great resource for understanding scholarship in clinical research.  Will need to verify data model (draw a Vue figure, run it through ontology groups), then gather data, map, test.
1. Implement American Universities data management in `uf_examples`. American Universities is a web site at UF used to list "all" accredited universities in the United States offering bachelor's degrees and above.  See http://clas.ufl.edu/au 
    1. Create separate def for american universities.  Web address, name, type
    2. Add `rdf:type` for american universities to UF VIVO
    3. Add python script for producing american universities web insert
As a UF Example. It uses a UF ontology extension
1. Refactor the CSV object as a true class.  Rewrite all CSV access.  Class should support column order and empty datasets.
