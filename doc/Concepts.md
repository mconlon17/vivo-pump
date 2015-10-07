One of the great advantages of VIVO is its ability to use controlled vocabularies to manage concepts across domains.
Your grants, papers, fields of study, personal research areas and others can all be coded using vocabularies that are
appropriate for the job.

Managing concepts in Simple VIVO is straightforward.  You edit concepts in concepts.txt as a spreadsheet.  You use
update to update VIVO.  You use get to retrieve concepts from your VIVO.

## Get started

Run `make_enum.txt` to create an enumeration of the concepts in your VIVO.  This will allow you to use concept labels
in your spreadsheet to refer to concepts that are "narrower" or "broader" than the concept you are editing.

```
python make_enum.txt
```

## Get Concepts from VIVO

Use

    python sv.py -a get
    
## Edit your Concepts

Use a spreadsheet program such as Excel or Numbers to open `concepts.txt` Edit and save.
 
## Update your VIVO

Use

    python sv.py -a update

Each time you wish to update your concepts -- add new concepts, add narrower or broader concepts to existing concepts, change the labels of concepts -- you can repeat the steps above: 

1. update the enumerations using `make_enum`
1. get the concepts from your VIVO into a spreadsheet using `sv.py -a get`
1. edit the concepts using a spreadsheet program
1. update VIVO using `sv.py -a update`