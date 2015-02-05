#!/usr/bin/env/python

"""
    read_update.py: Read an update definition from a file.

"""

__author__ = "Michael Conlon"
__copyright__ = "Copyright 2015, University of Florida"
__license__ = "New BSD License"
__version__ = "0.01"


class PathLengthException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def write_update_def(filename):
    """
    Write the UPDATE_DEF global to a json_file
    :param filename: name of file to write
    :return: None.  A file is written
    """
    import json
    out_file = open(filename, "w")
    json.dump(UPDATE_DEF, out_file, indent=4)
    out_file.close()
    return


def rec(current_object):
    if isinstance(current_object, dict):
        yield current_object["id"]
        for item in rec(current_object["children"]):
            yield item
    elif isinstance(current_object, list):
        for items in current_object:
            for item in rec(items):
                yield item


def read_update_def(filename):
    """
    Read an update_def from a file
    :param filename: name of file to read
    :return: JSON object from file
    """

    def fixit(current_object):
        from rdflib import URIRef
        if isinstance(current_object, dict):
            for k, t in current_object.items():
                if isinstance(t, basestring) and t.startswith('http://'):
                    current_object[k] = URIRef(t)
                else:
                    current_object[k] = fixit(current_object[k])
        elif isinstance(current_object, list):
            for i in range(0, len(current_object)):
                    current_object[i] = fixit(current_object[i])
        elif isinstance(current_object, basestring):
            if current_object.startswith("http://"):
                current_object = URIRef(current_object)
        return current_object

    import json
    in_file = open(filename, "r")
    update_def = fixit(json.load(in_file))
    return update_def

# Main Program

from json import dumps

the_update_structure = read_update_def("update_def.json")   # Read serialized, convert to URIRef as needed
print the_update_structure                                  # Shows the URIRef entries
print dumps(the_update_structure, indent=4)                 # everything serialized