class NotFound(Exception):
    pass


class TimeOut(Exception):
    pass


class NoLastNameForAuthor(Exception):
    pass


def get_entrez_record(pmid):
    """
    Given a pmid, use Entrez to get first record from PubMed
    """
    Entrez.email = 'mconlon@ufl.edu'

    # Get record(s) from Entrez.  Retry if Entrez does not respond

    start = 2.0
    retries = 10
    count = 0
    while True:
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
            records = Entrez.parse(handle)
            for record in records:
                pass
            break
        except IOError:
            count = count + 1
            if count > retries:
                raise Timeout
            sleep_seconds = start**count
            print "<!-- Failed Entrez query. Count = "+str(count)+ \
                " Will sleep now for "+str(sleep_seconds)+ \
                " seconds and retry -->"
            sleep(sleep_seconds) # increase the wait time with each retry
    return record


def author_case(author):
    """
    Given author name parts in an author dictionary, compute and return the
    case used in author finding by name:

    Case 0 last name only
    Case 1 last name, first initial
    Case 2 last name, first name
    Case 3 last name, first initial, middle initial
    Case 4 last name, first initial, middle name
    Case 5 last name, first name, middle initial
    Case 6 last name, first name, middle name
    """
    if 'first' in author and author['first'] is not None:
        fn = author['first']
    else:
        fn = ''
    if 'middle' in author and author['middle'] is not None:
        mn = author['middle']
    else:
        mn = ''
    if 'last' in author and author['last'] is not None:
        ln = author['last']
    else:
        ln = ''
    if ln == '':
        raise NoLastNameForAuthor(author)
    elif len(fn) > 1 and len(mn) > 1:
        return 6
    elif len(fn) > 1 and len(mn) == 1:
        return 5
    elif len(fn) == 1 and len(mn) > 1:
        return 4
    elif len(fn) == 1 and len(mn) == 1:
        return 3
    elif len(fn) > 1 and len(mn) == 0:
        return 2
    elif len(fn) == 1 and len(mn) == 0:
        return 1
    elif len(fn) == 0 and len(mn) == 0:
        return 0
    return case


def author_queries(case, author):
    """
    Given a case number and an author, return a list of queries to try
    to find the author in VIVO by name
    """
    query_set = {
        "0": [],
        "1": [1],
        "2": [4,1],
        "3": [2,1],
        "4": [3,2,1],
        "5": [5,4,3,2,1],
        "6": [6,5,4,3,2,1]
        }
    qs = query_set[str(case)]
    query_list = []
    for q in qs:
        query_list.append(author_case_query(q, author))
    return query_list


def author_case_query(qn, author):
    """
    Given a query number and an author, return a query for finding author
    in VIVO
    """
    if qn == 1:
        query = """
        SELECT ?uri
        WHERE {
            ?uri foaf:lastName "{{ln}}" .
            ?uri a ufVivo:UFCurrentEntity .
            ?uri foaf:firstName ?fn .
            FILTER(regex(?fn,"^{{fni}}"))
        }
        """
        query = query.replace('{{ln}}', author['last'])
        query = query.replace('{{fni}}', author['first'][0])
    elif qn == 2:
        query = """
        SELECT ?uri
        WHERE {
            ?uri foaf:lastName "{{ln}}" .
            ?uri a ufVivo:UFCurrentEntity .
            ?uri foaf:firstName ?fn .
            FILTER(regex(?fn,"^{{fni}}"))
            ?uri bibo:middleName ?mn .
            FILTER(regex(?fn,"^{{mni}}"))
        }
        """
        query = query.replace('{{ln}}', author['last'])
        query = query.replace('{{fni}}', author['first'][0])
        query = query.replace('{{mni}}', author['middle'][0])
    elif qn == 3:
        query = """
        SELECT ?uri
        WHERE {
            ?uri foaf:lastName "{{ln}}" .
            ?uri bibo:middleName "{{mn}}" .
            ?uri a ufVivo:UFCurrentEntity .
            ?uri foaf:firstName ?fn .
            FILTER(regex(?fn,"^{{fni}}"))
        }
        """
        query = query.replace('{{ln}}', author['last'])
        query = query.replace('{{fni}}', author['first'][0])
        query = query.replace('{{mn}}', author['middle'])
    elif qn == 4:
        query = """
        SELECT ?uri
        WHERE {
            ?uri foaf:lastName "{{ln}}" .
            ?uri foaf:firstName "{{fn}}" .
            ?uri a ufVivo:UFCurrentEntity .
        }
        """
        query = query.replace('{{ln}}', author['last'])
        query = query.replace('{{fn}}', author['first'])
    elif qn == 5:
        query = """
        SELECT ?uri
        WHERE {
            ?uri foaf:lastName "{{ln}}" .
            ?uri foaf:firstName "{{fn}}" .
            ?uri a ufVivo:UFCurrentEntity .
            ?uri bibo:middleName ?mn .
            FILTER(regex(?mn,"^{{mni}}"))
        }
        """
        query = query.replace('{{ln}}', author['last'])
        query = query.replace('{{fn}}', author['first'])
        query = query.replace('{{mni}}', author['middle'][0]) 
    elif qn == 6:
        query = """
        SELECT ?uri
        WHERE {
            ?uri foaf:lastName "{{ln}}" .
            ?uri a ufVivo:UFCurrentEntity .
            ?uri foaf:firstName "{{fn}}" .
            ?uri bibo:middleName "{{mn}}" .
        }
        """
        query = query.replace('{{ln}}', author['last'])
        query = query.replace('{{fn}}', author['first'])
        query = query.replace('{{mn}}', author['middle'])
    return query


def find_author(author):
    """
    Given an author object with name parts, return the smallest set of uris
    that match the author in VIVO.  Could be an empty set, could be a singleton,
    could be a clutch requiring further disambiguation
    """
    case = author_case(author)
    queries = author_queries(case, author)
    author_uri_set = set([])
    for query in queries:
        result = vivo_sparql_query(query.encode('utf-8'))
        count = len(result['results']['bindings'])
        if count == 1:
            author_uri_set = set([result['results']['bindings'][0]\
                                  ['uri']['value']])
            break
        elif count > 1 and count < len(author_uri_set):
            author_uri_set = set([])
            for row in result['results']['bindings']:
                author_uri_set.add(row['uri']['value'])
    return author_uri_set


def make_authorship_rdf(pub_uri, author_uri, rank, corresponding=False):
    """
    Given data values, create the RDF for an authorship
    """
    ardf = ""
    authorship_uri = get_vivo_uri()
    add = assert_resource_property(authorship_uri, "rdf:type", 
        untag_predicate("owl:Thing"))
    ardf = ardf + add
    add = assert_resource_property(authorship_uri, "rdf:type",
        untag_predicate("vivo:Authorship"))
    ardf = ardf + add
    add = assert_resource_property(authorship_uri,
        "vivo:linkedAuthor", author_uri)
    ardf = ardf + add
    add = assert_resource_property(authorship_uri,
        "vivo:linkedInformationResource", pub_uri)
    ardf = ardf + add
    add = assert_data_property(authorship_uri,
        "vivo:authorRank", rank)
    ardf = ardf + add
    add = assert_data_property(authorship_uri,
        "vivo:isCorrespondingAuthor", str(corresponding).lower())
    ardf = ardf + add
    return [ardf, authorship_uri]


def make_journal_rdf(name, issn):
    """
    Given a journal name and an issn, create the RDF for the journal
    """
    ardf = ""
    journal_uri = get_vivo_uri()
    add = assert_resource_property(journal_uri, "rdf:type", 
        untag_predicate("owl:Thing"))
    ardf = ardf + add
    add = assert_resource_property(journal_uri, "rdf:type",
        untag_predicate("bibo:Journal"))
    ardf = ardf + add
    add = assert_data_property(journal_uri, "rdfs:label", name)
    ardf = ardf + add
    add = assert_data_property(journal_uri, "bibo:issn", issn)
    ardf = ardf + add
    return [ardf, journal_uri]


def make_author_rdf(author):
    """
    Given an author structure, make a foaf:Person
    """
    ardf = ""
    author_uri = get_vivo_uri()
    add = assert_resource_property(author_uri, "rdf:type", 
        untag_predicate("owl:Thing"))
    ardf = ardf + add
    add = assert_resource_property(author_uri, "rdf:type",
        untag_predicate("foaf:Person"))
    ardf = ardf + add
    name = author['last'] + ', ' + author['first']
    if author.get('middle', None) is not None and len(author['middle']) > 0:
        name = name + ' ' + author['middle']
        add = assert_data_property(author_uri, "bibo:middleName",
                                   author['middle'])
        ardf = ardf + add
    add = assert_data_property(author_uri, "rdfs:label", name)
    ardf = ardf + add
    add = assert_data_property(author_uri, "foaf:lastName", author['last'])
    ardf = ardf + add
    add = assert_data_property(author_uri, "foaf:firstName", author['first'])
    ardf = ardf + add
    return [ardf, author_uri]


def make_pub_rdf(pub):
    """
    Given a pub structure, make VIVO RDF for the publication
    """
    properties = {'title': 'rdfs:label',
                  'volume': 'bibo:volume',
                  'issue': 'bibo:number',
                  'pmid': 'bibo:pmid',
                  'doi': 'bibo:doi',
                  'page_start': 'bibo:pageStart',
                  'page_end': 'bibo:pageEnd',
                  'date_harvested': 'ufVivo:dateHarvested',
                  'harvested_by': 'ufVivo:harvestedBy'}
    resources = {'journal_uri': 'vivo:hasPublicationVenue',
                 'date_uri': 'vivo:dateTimeValue'}
    ardf = ""
    pub_uri = pub['pub_uri']
    add = assert_resource_property(pub_uri, "rdf:type", 
        untag_predicate("owl:Thing"))
    ardf = ardf + add
    add = assert_resource_property(pub_uri, "rdf:type",
        untag_predicate("bibo:AcademicArticle"))
    ardf = ardf + add

    for property in sorted(properties.keys()):
        if property in pub:
            add = assert_data_property(pub_uri,
                properties[property],
                pub[property])
            ardf = ardf + add
    for resource in sorted(resources.keys()):
        if resource in pub:
            add = assert_resource_property(pub_uri,
                resources[resource],
                pub[resource])
            ardf = ardf + add

    for authorship_uri in pub['authorship_uris']:
        add = assert_resource_property(pub_uri,
            "vivo:informationResourceInAuthorship", authorship_uri)
        ardf = ardf + add
     
    return [ardf, pub_uri]


def get_pubmed(pmid, author_uris = None):
    """
    Given a pubmid identifer, return a structure containing the elements
    of the publication of interest to VIVO. Optionally, provide a set of
    author_uris for use in disambiguation.  When find_author returns a
    set of size > 1, the author_uris will be examined for matches to
    assist with disambiguation.
    """
    ardf = ""
    record = get_entrez_record(pmid)
    if record is None:
        return ["", None]
    pub = document_from_pubmed(record)
    if pub['page_end'] == '':
        pub['page_end'] = pub['page_start']
    if pub['date']['month'] == '':
        pub['date']['month'] = '1'
    if pub['date']['day'] == '':
        pub['date']['day'] = '1'
    pub['pub_uri'] = get_vivo_uri()
    pub['date_harvested'] = str(datetime.now())
    pub['harvested_by'] = "Python PubMed Add "+__version__
    journal_uri = find_vivo_uri("bibo:issn", pub['issn'])
    if journal_uri is None:
        [add, journal_uri] = make_journal_rdf(pub['journal'], pub['issn'])
        ardf = ardf + add
    pub['journal_uri'] = journal_uri

    pub_date = datetime.strptime(pub['date']['month']+'/'+pub['date']['day']+\
                                 '/'+pub['date']['year'], "%m/%d/%Y")
    if pub_date in date_dictionary:
        pub['date_uri'] = date_dictionary[pub_date]
    else:
        [add, pub_date_uri] = make_datetime_rdf(pub_date.isoformat())
        date_dictionary[pub_date] = pub_date_uri
        pub['date_uri'] = pub_date_uri
        ardf = ardf + add
        
#   Turn each author into a URI reference to an authorship

    pub['authorship_uris'] = []
    for key, author in sorted(pub['authors'].items(),key=lambda x:x[0]):
        try:
            author_uri_set = find_author(author)
        except:
            print "No last name for author", author
            print "Pub\n", pub
            print "Record\n", record
            continue
        if len(author_uri_set) == 0:
            [add, author_uri] = make_author_rdf(author)
            ardf = ardf + add
            print pmid, "Add", author, "at", author_uri
        elif len(author_uri_set) == 1:
            author_uri = list(author_uri_set)[0]
            print pmid, "Found", author, author_uri
        else:
            if author_uris is None:
                author_uri = list(author_uri_set)[0]
                print pmid, "Disambiguate", author, "from", author_uri_set
            else:
                possible_uri_set = author_uri_set.intersection(author_uris)
                if len(possible_uri_set) == 1:
                    author_uri = list(possible_uri_set)[0]
                else:
                    author_uri = list(possible_uri_set)[0]
                    print pmid, "Disambiguate", author, "from", possible_uri_set
            print "Disambiguate:"
            print "  Possible authors in VIVO", author_uri_set
            print "  Possible authors in Source", author_uris
            print "  Selected author", author_uri
                    
        [add, authorship_uri] = make_authorship_rdf(pub['pub_uri'], author_uri,
                                                    key, corresponding=False)
        pub['authorship_uris'].append(authorship_uri)
        ardf = ardf + add
    
    return [ardf, pub]


def prepare_pubs(path_name):
    """
    Read the list of pubs to add.  For each, process the ufid field into a
    set of VIVO uris.  The ufid field is optionally a semi-colon delimited
    list of either ufids or uris.  The result will be a set of uris.  These
    uris are compared to uris in disambiguation sets to select authors.
    """
    add_pubs = read_csv(path_name)
    for key, row in add_pubs.items():
        row['author_uris'] = set([])
        ids = row['ufid'].split(';')
        print "ids=", ids
        for id in ids:
            print "Processing id=", id
            if id[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                author_uri = find_vivo_uri('ufVivo:ufid', id)
                if author_uri is None:
                    print >>exc_file, id, "UFID not found in VIVO"
                    continue
                else:
                    row['author_uris'].add(author_uri)
            elif id[0] == 'h':
                row['author_uris'].add(id)
            else:
                print >>exc_file, row['ufid'], "Unknown identifier in UFID"
            print id, row
        add_pubs[key] = row
    return add_pubs