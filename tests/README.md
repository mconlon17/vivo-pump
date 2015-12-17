# Unit Tests and Data for VIVO Pump

## Unit Tests

Test cases are in `test_vivopump.py`.  Test data are in the data folder.

Many of the cases use a synthetic graph named `TestGraph`, imported from `testgraph.py`

A few examples go to a "live" VIVO to get data.  Examples using `query_parms` are those that require a live VIVO 
with connection string, username and password to access.  You will need to provide a live VIVO and modify the query
parameters as appropriate for your VIVO to run these tests successfully.

## Command line tests

`test_sv.py` runs a series of Simple VIVO tests.  The tests are specified using command line arguments.  Each of the
 examples can be run, testing `get` and `update` for each.  Additional tests exercise the command line parameters.
 
 The output of `test_sv.py` is a tab delimited data of test results.  Each row is the result of one test.  The data
 elements in each row are the test name, the return code for the test (0=pass, 1=fail), and the time in seconds to
 perform the test.
 
 Simple output is shown below:
 
              config not found 	1 	0.110546
     definition file not found 	1 	0.04471
                          help 	0 	0.050342
         source file not found 	1 	0.111886
                          test 	0 	1.009888
                          
 The "not found" tests have return codes of "1" as expected.                        