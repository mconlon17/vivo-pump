#!/usr/bin/env python
# coding=utf-8
"""
    test_sv.py -- Test cases for Simple VIVO
"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015 (c) Michael Conlon"
__license__ = "New BSD license"
__version__ = "1.00"


def run_tests(tests):
    """
    Run a series of tests.  Produce timing for each
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
    Run tests, print results
    :return: None
    """
    tests = {
        "summarize": "python ../sv.py -a summarize",
        "serialize": "python ../sv.py -a serialize",
        "update   ": "python ../sv.py -a update",
        "get      ": "python ../sv.py -a get",
        "help     ": "python ../sv.py -h",
        "test     ": "python ../sv.py -a test"
    }
    test_results = run_tests(tests)
    for testid in sorted(test_results):
        print testid, "\t", test_results[testid][0], "\t", test_results[testid][1]


if __name__ == "__main__":
    main()
