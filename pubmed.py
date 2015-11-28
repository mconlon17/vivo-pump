#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pubmed -- identify and retrieve pubmed publications for a person.  Handle those publications in the pump
"""

import logging
import sys
import httplib

__author__ = "Michael Conlon"
__copyright__ = "Copyright (c) 2015 Michael Conlon"
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


def get_pmids(first, middle, last, email, affiliation=None, yes=None, no=None):
    """
    Given an author's identifiers and affiliation information, optional lists of pmids, call the catalyst service
    to retrieve PMIDS for the author and return a list of PMIDS
    :param first: author first name
    :param middle: author middle name
    :param last: author last name
    :param email: author email(s) as a list
    :param affiliation: author affiliation as a list
    :param yes: list of pmids written by the author
    :param no: list of pmids not written by the author
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
