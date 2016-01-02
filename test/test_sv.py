#!/usr/bin/env python
# coding=utf-8
"""
    test_sv.py -- Test cases for Simple VIVO
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2016 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "1.00"


def run_tests(tests):
    """
    Run a series of test.  Produce timing for each
    :return: dictionary of test timings keyed by test id.
    """
    from datetime import datetime
    from subprocess import call

    test_timings = {}
    for test_id in tests:
        start = datetime.now()
        try:
            rc = call(tests[test_id], shell=True)
        except OSError as error_thing:
            rc = str(error_thing)
        end = datetime.now()
        elapsed = (end - start).total_seconds()
        test_timings[test_id] = [rc, elapsed]
    return test_timings


def main():
    """
    Run test, print results
    :return: None
    """
    tests = {
        # "summarize": "python ../sv.py -a summarize",
        # "serialize": "python ../sv.py -a serialize",
        # "update": "python ../sv.py -a update",
        # "get": "python ../sv.py -a get -s get.txt",
        "help": "python ../sv.py -h",
        "test": "python ../sv.py -a test",
        "config not found": "python ../sv.py -a update -c data/cfg_not_found.cfg",
        "source file not found": "python ../sv.py -a update -s data/no_such_source_file.txt",
        "definition file not found": "python ../sv.py -a update -d data/no_such_definition_file.cfg",
        # "invalid access": "python ../sv.py -a test -c data/invalid_access.cfg",
        # "invalid JSON": "python ../sv.py -a update -d data/grant_invalid_def.json",
        # "awards get": "cd ../examples/awards; python ../../sv.py -a get -s get.txt",
        # "awards update": "cd ../examples/awards; python ../../sv.py -a update",
        # "concepts get": "cd ../examples/concepts; python ../../sv.py -a get -s get.txt",
        # "concepts update": "cd ../examples/concepts; python ../../sv.py -a update",
        # "courses get": "cd ../examples/courses; python ../../sv.py -c sv_courses.cfg -a get -s get.txt",
        # "courses update": "cd ../examples/courses; python ../../sv.py -c sv_courses.cfg -a update",
        # "teaching get": "cd ../examples/courses; python ../../sv.py -a get -s get.txt",
        # "teaching update": "cd ../examples/courses; python ../../sv.py -a update",
        # "dates get": "cd ../examples/dates; python ../../sv.py -a get -s get.txt",
        # "dates update": "cd ../examples/dates; python ../../sv.py -a update",
        # "education get": "cd ../examples/education; python ../../sv.py -a get -s get.txt",
        # "education update": "cd ../examples/education; python ../../sv.py -a update",
        # "grants get": "cd ../examples/grants; python ../../sv.py -a get -s get.txt",
        # "grants update": "cd ../examples/grants; python ../../sv.py -a update",
        # "journals get": "cd ../examples/journals; python ../../sv.py -a get -s get.txt",
        # "journals update": "cd ../examples/journals; python ../../sv.py -a update",
        # "locations get": "cd ../examples/locations; python ../../sv.py -a get -s get.txt",
        # "locations update": "cd ../examples/locations; python ../../sv.py -a update",
        # "orgs get": "cd ../examples/orgs; python ../../sv.py -a get -s get.txt",
        # "orgs update": "cd ../examples/orgs; python ../../sv.py -a update",
        # "people get": "cd ../examples/people; python ../../sv.py -a get -s get.txt",
        # "people update": "cd ../examples/people; python ../../sv.py -a update",
        # "positions get": "cd ../examples/positions; python ../../sv.py -a get -s get.txt",
        # "positions update": "cd ../examples/positions; python ../../sv.py -a update"
    }
    test_results = run_tests(tests)
    for testid in sorted(test_results):
        print testid.rjust(1 + max([len(x) for x in tests.keys()])), '\t', test_results[testid][0], "\t", \
            test_results[testid][1]


if __name__ == "__main__":
    main()
