def catalyst_pmid_request(first, middle, last, email, debug=False):
    """
    Given an author name at the University of Florida, return the PMIDs of
    papers that are likely to be the works of the author.  The Harvard
    Catalyst GETPMIDS service is called.

    Uses HTTP XML Post request, by www.forceflow.be
    """
    request = tempita.Template("""
        <?xml version="1.0"?>
        <FindPMIDs>
            <Name>
                <First>{{first}}</First>
                <Middle>{{middle}}</Middle>
                <Last>{{last}}</Last>
                <Suffix/>
            </Name>
            <EmailList>
                <email>{{email}}</email>
            </EmailList>
            <AffiliationList>
                <Affiliation>%university of florida%</Affiliation>
                <Affiliation>%@ufl.edu%</Affiliation>
            </AffiliationList>
            <LocalDuplicateNames>1</LocalDuplicateNames>
            <RequireFirstName>false</RequireFirstName>
            <MatchThreshold>0.98</MatchThreshold>
        </FindPMIDs>""")
    HOST = "profiles.catalyst.harvard.edu"
    API_URL = "/services/GETPMIDs/default.asp"
    request = request.substitute(first=first, middle=middle, last=last, \
        email=email)
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
    if debug:
        print "Request", request
        print "StatusCode, Messgage,header", statuscode, statusmessage, header
        print "result", result
    return result
