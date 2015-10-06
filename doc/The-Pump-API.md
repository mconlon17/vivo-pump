The Pump API is the collection of exposed elements that define how other software and users interact with the Pump.

The Pump API consists of:

1. [The Pump arguments](https://github.com/mconlon17/vivo-pump/wiki/pump-arguments).  All the things that are set by 
default and/or are available to the programmer and the user
to set to define the actions of the Pump.  All arguments are accessible via command line arguments of the main program
`sv` (Simple VIVO) which is used to call the Pump.
1. [The Pump methods and instance variables](https://github.com/mconlon17/vivo-pump/wiki/pump-api).  Pump methods and 
instance variables are accessible to the programmer and so constitute part of the Pump API.
1. [The Pump Definition file](https://github.com/mconlon17/vivo-pump/wiki/pump-definition-file).  Each Pump requires a 
definition file, in JSON format, to define the transformations the Pump will perform to and from the flat file 
representation to the semantic web representation.

Elements of the distribution that do not constitute parts of the Pump API, include **everything else**, including, 
but not limited to:

1.  Data
1.  Examples
1.  The `vivopump` library, which consists of functions used by the Pump.
1.  Test cases
1.  Config files
1.  Documentation files

Definition of the Pump API is critical for understanding [Semantic Versioning](http://semver.org) used in the Pump.