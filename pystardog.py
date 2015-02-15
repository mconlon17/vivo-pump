#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To query over a Stardog server, initialize a StardogClient object then invoke :func:`query`.
Results are encapsulated in a :class:`ResultsParser` instance::

    >>> client = StardogClient(server_endpoint)
    >>> client.set_database(database_name)
    >>> result = client.query(query)
    >>> for row in result:
    >>>     print row
"""

__version__ = "0.1"
__author__ = "Huy Phan"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Huy Phan"]
__license__ = "MPL"
__maintainer__ = "Huy Phan"
__email__ = "dachuy@gmail.com"
__status__ = "Production"


import httplib, urllib
from urlparse import urlparse
from xml.dom import pulldom
import re

try:
    import json
except ImportError:
    import simplejson as json

import struct

USER_AGENT = "stardog-client/%s" % __version__

CONTENT_TYPE = {
                 'turtle' : "application/turtle" ,
                 'n3' :"application/n3",
                 'rdfxml' : "application/rdf+xml" ,
                 'ntriples' : "application/n-triples" ,
                 'xml' : "application/xml"
                }

RESULTS_TYPES = {
                 'xml' : "application/sparql-results+xml" ,
                 'json' : "application/sparql-results+json",
                 'binary-table': "application/x-binary-rdf-results-table"
                 }

REASONING_TYPES = ["DL", "EL", "QL", "RL", "RDFS", None]

# The purpose of this construction is to use shared strings when
# they have the same value. This way comparisons can happen on the
# memory address rather than looping through the content.
XSD_STRING = 'http://www.w3.org/2001/XMLSchema#string'
XSD_INTEGER = 'http://www.w3.org/2001/XMLSchema#integer'
XSD_LONG = 'http://www.w3.org/2001/XMLSchema#long'
XSD_DOUBLE = 'http://www.w3.org/2001/XMLSchema#double'
XSD_FLOAT = 'http://www.w3.org/2001/XMLSchema#float'
XSD_DECIMAL = 'http://www.w3.org/2001/XMLSchema#decimal'
XSD_DATETIME = 'http://www.w3.org/2001/XMLSchema#dateTime'
XSD_DATE = 'http://www.w3.org/2001/XMLSchema#date'
XSD_TIME = 'http://www.w3.org/2001/XMLSchema#time'
XSD_BOOLEAN = 'http://www.w3.org/2001/XMLSchema#boolean'

datatype_dict = {
                 '': '',
                 XSD_STRING : XSD_STRING,
                 XSD_INTEGER : XSD_INTEGER,
                 XSD_LONG : XSD_LONG,
                 XSD_DOUBLE : XSD_DOUBLE,
                 XSD_FLOAT : XSD_FLOAT,
                 XSD_DECIMAL : XSD_DECIMAL,
                 XSD_DATETIME : XSD_DATETIME,
                 XSD_DATE : XSD_DATE,
                 XSD_TIME : XSD_TIME,
                 XSD_BOOLEAN : XSD_BOOLEAN
                 }

_n3_quote_char = re.compile(r'[^ -~]|["\\]')
_n3_quote_map = {
    '"': '\\"',
    '\n': '\\n',
    '\t': '\\t',
    '\\': '\\\\',
}

def _n3_quote(string):
    def escape(m):
        ch = m.group()
        if ch in _n3_quote_map:
            return _n3_quote_map[ch]
        else:
            return "\\u%04x" % ord(ch)
    return '"' + _n3_quote_char.sub(escape, string) + '"'

def Datatype(value):
    """
    Replace the string with a shared string.
    intern() only works for plain strings - not unicode.
    We make it look like a class, because it conceptually could be.
    Notice: This code is reused from sparql-client-0.9
    """
    if value==None:
        r = None
    elif datatype_dict.has_key(value):
        r = datatype_dict[value]
    else:
        r = datatype_dict[value] = value
    return r

class RDFTerm(object):
    """
    Super class containing methods to override. :class:'IRI',
    :class:'Literal' and :class:'BlankNode' all inherit from :class:'RDFTerm'.
    Notice: This code is reused from sparql-client-0.9
    """

    __allow_access_to_unprotected_subobjects__ = {'n3': 1}

    def __str__(self):
        return str(self.value)

    def __unicode__(self):
        return self.value

    def n3(self):
        """ Return a Notation3 representation of this term. """
        # To override
        # See N-Triples syntax: http://www.w3.org/TR/rdf-testcases/#ntriples
        raise NotImplementedError("Subclasses of RDFTerm must implement 'n3'")

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.n3())

class IRI(RDFTerm):
    """
    An RDF resource.
    Notice: This code is reused from sparql-client-0.9
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
       return self.value.encode("unicode-escape")

    def __eq__(self, other):
       if type(self) != type(other):
           return False
       if self.value == other.value: return True
       return False

    def n3(self):
        return '<%s>' % self.value

class Literal(RDFTerm):
    """
    Literals. These can take a data type or a language code.
    Notice: This code is reused from sparql-client-0.9
    """
    def __init__(self, value, datatype=None, lang=None):
        self.value = unicode(value)
        self.lang = lang
        self.datatype = datatype

    def __eq__(self, other):
       if type(self) != type(other):
           return False

       elif (self.value == other.value and
             self.lang == other.lang and
             self.datatype == other.datatype):
           return True

       else:
           return False

    def n3(self):
        n3_value = _n3_quote(self.value)

        if self.datatype is not None:
            n3_value += '^^<%s>' % self.datatype

        if self.lang is not None:
            n3_value += '@' + self.lang

        return n3_value

class BlankNode(RDFTerm):
    """
    Blank node. Similar to 'IRI' but lacks a stable identifier.
    Notice: This code is reused from sparql-client-0.9
    """
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
       if type(self) != type(other):
           return False
       if self.value == other.value:
           return True
       return False

    def n3(self):
        return '_:%s' % self.value

class StardogClient(object):
    """
    Main class of the library.
    """

    def __init__(self, server_url):
        """
        Ininitialize a Stardog client, users need to pass a Stardog endpoint URL
        """
        if not server_url.startswith("http://"):
            server_url = "http://" + server_url
        self._server_url = server_url
        self._database = None
        self._reasoning = None
        self._method = "POST"
        self._result_type = 'binary-table'

        self._http_headers = {
            'Accept' : RESULTS_TYPES[self._result_type],
            'User-Agent' : USER_AGENT,
#            'SD-Protocol' : '1.0.3',
            'SD-Connection-String': None
        }

        o = urlparse(server_url)
        self._server_hostname, self._server_port = o.hostname, o.port

    def set_database(self, database):
        """
        Set database to be used
        """
        self._database = database
        self.__update_connection_string()

    def set_reasoning(self, reasoning):
        """
        Set reasoning type, accepted values: 'DL', 'EL', 'QL', 'RL', 'RDFS', 'None' (default)
        """
        self._reasoning = reasoning
        self.__update_connection_string()

    def set_result_type(self, result_type):
        """
        Set content type of result, accepted values: 'xml', 'json', 'binary-table' (default)
        """
        if not RESULTS_TYPES.has_key(result_type):
            raise Exception("Invalid result type: %s" % result_type)
        self._result_type = result_type
        self._http_headers['Accept'] = RESULTS_TYPES[result_type]

    def set_http_method(self, method):
        """
        Set HTTP Method, accepted values: 'POST' or 'GET'
        """
        if method not in ["POST", "GET"]:
            raise Exception("Invalid HTTP method: %s" % method)
        self._method = method

    def __update_connection_string(self):
        self._http_headers['SD-Connection-String'] = "reasoning=%s;kb=%s;persist=sync" % (self._reasoning, self._database)

    def query(self, sparql_query):
        """
        Construct and send HTTP request to Stardog server
        """
        if self._database == None:
            raise Exception("Database undefined")

        conn = httplib.HTTPConnection(self._server_hostname, self._server_port)
        params = {
            "query" : sparql_query,
            "username": "admin",
            "password": "admin"
        }
        query_path = "/%s/query" % self._database

        conn.request(self._method, query_path, urllib.urlencode(params), self._http_headers)
        response = conn.getresponse()
        print response.status
        if response.status != 200:
            raise Exception("Request failed: %s" % response.status)

        parser = ResultParser.get_parser(self._result_type)
        return parser(response)


class ResultParser(object):

    """
    Base class of all result parsers
    """
    def __init__(self):
        self._iter = None

    @staticmethod
    def get_parser(result_type):
        if not RESULTS_TYPES.has_key(result_type):
            raise Exception("Invalid result type: %s" % result_type)

        if result_type == 'xml':
            return XMLResultParser
        elif result_type == 'json':
            return JSONResultParser
        elif result_type == 'binary-table':
            return BinaryTableResultParser

    def hasresult(self):
        """
        ASK queries are used to test if a query would have a result.  If the
        query is an ASK query there won't be an actual result, and
        :func:'fetchone' will return nothing. Instead, this method can be
        called to check the result from the ASK query.

        If the query is a SELECT statement, then the return value of
        :func:'hasresult' is 'None', as the XML result format doesn't tell you
        if there are any rows in the result until you have read the first one.
        """
        return self._hasResult

    def __iter__(self):
        if self._iter == None:
            self._iter = self.generator()
        return self._iter

    def fetchone(self):
        """ Synonim for :func:'fetchone'. """
        return iter(self).next()

    def fetchall(self):
        """ Loop through the result to build up a list of all rows.
            Patterned after DB-API 2.0.
        """
        result = []
        for row in self.generator():
            result.append(row)
        return result

    def fetchmany(self, num):
        result = []
        for row in self.generator():
            result.append(row)
            num -= 1
            if num <= 0: return result
        return result

class XMLResultParser(ResultParser):

    """
    Parse the XML result
    Notice: This code is reused from sparql-client-0.9 with some modifications
    """

    def __init__(self, fp):
        self._iter = None
        self._fp = fp
        vals = []
        self._hasResult = None
        self._variables = []
        self._fetchhead()

    def _fetchhead(self):
        """
        Fetches the head information. If there are no variables in the
        <head>, then we also fetch the boolean result.
        """
        self.events = pulldom.parse(self._fp)

        for (event, node) in self.events:
            if event == pulldom.START_ELEMENT:
                if node.tagName == 'variable':
                    self._variables.append(node.attributes['name'].value)
                elif node.tagName == 'boolean':
                    self.events.expandNode(node)
                    self._hasResult = (node.firstChild.data == 'true')
                elif node.tagName == 'result':
                    return # We should not arrive here
            elif event == pulldom.END_ELEMENT:
                if node.tagName == 'head' and self._variables:
                    return
                elif node.tagName == 'sparql':
                    return

    def generator(self):
        """ Fetches the next set of rows of a query result, returning a list.
            An empty list is returned when no more rows are available.
            If the query was an ASK request, then an empty list is returned as
            there are no rows available.
        """
        idx = None
        vals = None

        for (event, node) in self.events:
            if event == pulldom.START_ELEMENT:
                if node.tagName == 'result':
                    vals = {}
                elif node.tagName == 'binding':
                    idx = node.attributes['name'].value
                elif node.tagName == 'uri':
                    self.events.expandNode(node)
                    data = ''.join(t.data for t in node.childNodes)
                    vals[idx] = IRI(data)
                elif node.tagName == 'literal':
                    self.events.expandNode(node)
                    data = ''.join(t.data for t in node.childNodes)
                    lang = node.getAttribute('xml:lang') or None
                    datatype = Datatype(node.getAttribute('datatype')) or None
                    vals[idx] = Literal(data, datatype, lang)
                elif node.tagName == 'bnode':
                    self.events.expandNode(node)
                    data = ''.join(t.data for t in node.childNodes)
                    vals[idx] = BlankNode(data)

            elif event == pulldom.END_ELEMENT:
                if node.tagName == 'result':
                    #print "rtn:", len(vals), vals
                    yield vals

class JSONResultParser(ResultParser):

    """
    Parse the JSON result
    """

    def __init__(self, fp):
        self._iter = None
        self._hasResult = None
        results = json.loads(fp.read())
        if results.has_key('results'):
            self.data = iter(results['results']['bindings'])
        else:
            self.data = iter([])

    def generator(self):
        for row in self.data:
            for (key,value) in row.items():
                if value['type'] == 'uri':
                    row[key] = IRI(value.get('value'))
                elif value['type'] == 'typed-literal':
                    datatype = Datatype(value.get('datatype')) or None
                    lang = value.get('xml:lang') or None
                    row[key] = Literal(value.get('value'), datatype, lang)
                elif value['type'] == 'literal':
                    datatype = Datatype(value.get('datatype')) or None
                    row[key] = Literal(value.get('value'), datatype)
                elif value['type'] == 'bnode':
                    row[key] = BlankNode(value.get('value'))
            yield row

class BinaryTableResultParser(ResultParser):

    """
    Parse the Binary result
    """
    RT_NULL = 0
    RT_REPEAT = 1
    RT_NAMESPACE = 2
    RT_QNAME = 3
    RT_URI = 4
    RT_BNODE = 5
    RT_PLAIN_LITERAL = 6
    RT_LANG_LITERAL = 7
    RT_DATATYPE_LITERAL = 8
    RT_ERROR = 126
    RT_TABLE_END = 127

    def __init__(self, fp):
        self._iter = None
        self._hasResult = None
        self._variables = []
        self._fp = fp
        self.sanity_check()
        self.last = None

    def read_byte(self):
        return struct.unpack('b', self._fp.read(1))[0]

    def read_int(self):
        return struct.unpack('>i', self._fp.read(4))[0]

    def read_atom(self):
        size = self.read_int()
        return self._fp.read(size)

    """
    Verify signature of binary result and get version, columns information
    """
    def sanity_check(self):
        data = self._fp.read(12)
        sign, version, columns = struct.unpack('>4sii',data)
        if sign != 'BRTR':
            raise Exception("Invalid signature: %s" % sign)

        for i in range(columns):
            self._variables.append(self.read_atom())

        self.columns = columns

    def add(self, o):
        self.idx = (self.idx + 1) % self.columns
        self.vals[self._variables[self.idx % self.columns]] = o

    def add_last(self):
        if self.last == None:
            raise Exception("REPEAT variable with no previous row")

        self.idx = (self.idx + 1) % self.columns
        self.vals[self._variables[self.idx]] = self.last[self._variables[self.idx]]

    def generator(self):
        self.vals = {}
        self.idx = -1
        namespaces = {}

        done = False
        while not done:
            added = False
            record_type_marker = self.read_byte()
            if record_type_marker == self.RT_NULL:
                pass
            elif record_type_marker == self.RT_REPEAT:
                self.add_last()
                added = True
            elif record_type_marker == self.RT_NAMESPACE:
                ord = self.read_int()
                prefix = self.read_atom()
                namespaces[ord] = prefix
            elif record_type_marker == self.RT_QNAME:
                ord = self.read_int()
                localname = self.read_atom()
                self.add(IRI(namespaces[ord] + localname))
                added = True
            elif record_type_marker == self.RT_URI:
                iri = self.read_atom()
                self.add(IRI(iri))
                added = True
            elif record_type_marker == self.RT_BNODE:
                label = self.read_atom()
                self.add(BNode(label))
                added = True
            elif record_type_marker == self.RT_PLAIN_LITERAL:
                value = self.read_atom()
                self.add(Literal(value))
                added = True
            elif record_type_marker == self.RT_LANG_LITERAL:
                value = self.read_atom()
                lang = self.read_atom()
                self.add(Literal(value, lang))
                added = True
            elif record_type_marker == self.RT_DATATYPE_LITERAL:
                value = self.read_atom()
                b = self.read_byte()
                if b ==self.RT_QNAME:
                    ord = self.read_int()
                    localname = self.read_atom()
                    self.add(Literal(value, namespaces[ord] + localname))
                    added = True
                elif b ==self.RT_URI:
                    iri = self.read_atom()
                    self.add(Literal(value, iri))
                    added = True
                else:
                    raise Exception("Unknown atom type: %d" % record_type_marker)
            elif record_type_marker == self.RT_ERROR:
                error_type = self.read_byte()
                msg = self.read_atom()
                if error_type == 1:
                    raise Exception("Malformed query error: %s" % msg)
                elif error_type == 2:
                    raise Exception("Query evaluation error: %s" % msg)
                else:
                    raise Exception("Unknown error")
            elif record_type_marker == self.RT_TABLE_END:
                done = True
            else:
                raise Exception("Unknown atom type: %d" % record_type_marker)

            if added == True and self.idx == self.columns - 1:
                self.last = self.vals
                yield self.vals
