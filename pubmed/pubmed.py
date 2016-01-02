#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    pubmed.py -- tools for identifying pubmed papers, retrieving citation data for pubmed papers, and loading those
    papers into VIVO
"""

import logging
import sys
import httplib

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2016 Michael Conlon"
__license__ = "New BSD license"
__version__ = "0.8.5"

# Establish logging

logging.captureWarnings(True)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stderr)
# handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

#   Catalyst service access

HOST = "profiles.catalyst.harvard.edu"
API_URL = "/services/GETPMIDs/default.asp"


def get_person_catalyst_pmids(uri, query_parms):
    """
    Given a person uri, collect the attributes needed to call get_pmids and return two lists:
    a list of pubs for the person found in VIVO, and a list of pubs for the person found by
    the catalyst service
    :param uri: the uri of a person in VIVO
    :return: A dictionary of two lists, the vivo_pmids and the catalyst_pmids
    """
    from vivopump import vivo_query
    query = """
    SELECT ?first ?middle ?last ?email ?affiliation
    WHERE {
      <{}>
    }
    """
    query = query.format(uri)
    a = vivo_query(query, query_parms)
    first = a['results']['bindings'][0]['first']['value']
    middle = None
    last = None
    emails = None
    affiliations = None
    return get_catalyst_pmids(first, middle, last, emails, affiliations)


def get_person_vivo_pmids(uri, query_parms):
    """
    Given the uri of a person, query VIVO to get a list of the person's publications with pmids
    :param uri:
    :return: a dictionary keyed by pmid with uris of the pubs for each pmid
    """
    from pump.vivopump import vivo_query
    query = """SELECT (MAX(?paper_uri) AS ?puri) ?pmid
    WHERE {
        <{}> vivo:relatedBy ?a .
        ?a a vivo:Authorship .
        ?a vivo:relates ?paper_uri .
        ?paper_uri a bibo:AcademicArticle .
        ?paper_uri bibo:pmid ?pmid .
    }
    GROUP BY ?pmid
    """
    query = query.replace('{}', uri)
    a = vivo_query(query, query_parms)
    pmid = [x['pmid']['value'] for x in a['results']['bindings']]
    puri = [x['puri']['value'] for x in a['results']['bindings']]
    return dict(zip(pmid, puri))


def get_catalyst_pmids(first, middle, last, email, affiliation=None):
    """
    Given an author's identifiers and affiliation information, optional lists of pmids, call the catalyst service
    to retrieve PMIDS for the author and return a list of PMIDS
    :param first: author first name
    :param middle: author middle name
    :param last: author last name
    :param email: author email(s) as a list
    :param affiliation: author affiliation as a list
    :return: list of pmids identified by the catalyst service that have a high probability of being written by the
    author
    """
    from xml.dom.minidom import parseString  # tools for handling XML in python

    result = catalyst_getpmids_xml(first, middle, last, email, affiliation)
    dom = parseString(result)  # create a document Object Model (DOM) from the Harvard Catalyst result
    return [node.childNodes[0].data for node in dom.getElementsByTagName('PMID')]  # return a list of PMID values


def catalyst_getpmids_xml(first, middle, last, email, affiliation=None):
    """
    Given an author name, email(s) and optional affiliation(s), return the PMIDs of
    papers that are likely to be the works of the author.  The Harvard
    Catalyst GETPMIDS service is called.
    """
    request = """
        <?xml version="1.0"?>
        <FindPMIDs>
            <Name>
                <First>{}</First>
                <Middle>{}</Middle>
                <Last>{}</Last>
                <Suffix/>
            </Name>
            <EmailList>
                {}
            </EmailList>
            <AffiliationList>
                {}
            </AffiliationList>
            <LocalDuplicateNames>1</LocalDuplicateNames>
            <RequireFirstName>false</RequireFirstName>
            <MatchThreshold>0.98</MatchThreshold>
        </FindPMIDs>"""

    if affiliation is None:
        affiliation = []
    email_string = ''.join(['<Email>' + em + '</Email>' for em in email])
    affil_string = ''.join(['<Affiliation>' + aff + '</Affiliation>' for aff in affiliation])

    request = request.format(first, middle, last, email_string, affil_string)
    webservice = httplib.HTTP(HOST)
    webservice.putrequest("POST", API_URL)
    webservice.putheader("Host", HOST)
    webservice.putheader("User-Agent", "Python post")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(request))
    webservice.endheaders()
    webservice.send(request)
    statuscode, statusmessage, header = webservice.getreply()
    result = webservice.getfile().read()
    logger.debug(u"Request {}\n\tStatus Code {} Message {} Header {}\n\tResult {}".format(request, statuscode,
                                                                                          statusmessage, header,
                                                                                          result))
    return result
