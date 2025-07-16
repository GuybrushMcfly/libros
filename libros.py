from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://data.cervantesvirtual.com/bvmc-lod/repositories/data")
sparql.setQuery("""
PREFIX rdac: <http://rdaregistry.info/Elements/c/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?label
WHERE {
  <http://data.cervantesvirtual.com/person/40> ?rol ?m .
  ?m a rdac:Manifestation .
  ?m rdfs:label ?label
}
LIMIT 10
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
for r in results["results"]["bindings"]:
    print(r["label"]["value"])
