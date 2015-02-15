
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:5820/vivo/query")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://vivo.ufl.edu/individual/n25562> rdfs:label ?label }
""")
sparql.setReturnFormat(JSON)
sparql.setCredentials("anonymous", "anon")
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(result["label"]["value"])
