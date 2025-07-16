import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

ENDPOINT = "http://data.cervantesvirtual.com/bvmc-lod/repositories/data"

# Consultar obras (manifestaciones) de un autor
def consulta_obras_autor(persona_uri, limite=10):
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(f"""
    PREFIX rdac: <http://rdaregistry.info/Elements/c/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?m ?label WHERE {{
      <{persona_uri}> ?rol ?m .
      ?m a rdac:Manifestation .
      ?m rdfs:label ?label .
    }} LIMIT {limite}
    """)
    sparql.setReturnFormat(JSON)
    res = sparql.queryAndConvert()
    return [(b["m"]["value"], b["label"]["value"]) for b in res["results"]["bindings"]]

st.title("📚 Obras desde BVMC SPARQL")

# Selector manual de autor (uri + descripción)
opciones = {
    "Miguel de Cervantes Saavedra": "http://data.cervantesvirtual.com/person/40",
    "Gonzalo F. de Oviedo y Valdés": "http://data.cervantesvirtual.com/person/360"
}
autor_nombre = st.selectbox("Seleccione un autor:", list(opciones.keys()))
autor_uri = opciones[autor_nombre]

if st.button("Mostrar obras"):
    obras = consulta_obras_autor(autor_uri, limite=20)
    if obras:
        df = pd.DataFrame(obras, columns=["Manifestación (URI)", "Título"])
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(sortable=True, filter=True, editable=False)
        gb.configure_selection("single", use_checkbox=False)
        AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.NO_UPDATE,
               height=400, theme="alpine")
    else:
        st.warning("No se encontraron obras para este autor.")

# Ejemplos alternativos (Idiomas, Fechas)
st.markdown("---")
st.markdown("### 🧩 También puedes correr otras consultas SPARQL:")

st.code("""
# Idiomas ordenados por nº manifestaciones
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX madsrdf: <http://www.loc.gov/mads/rdf/v1#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT ?language (COUNT(?manifestation) AS ?count) ?code WHERE {
  ?language rdf:type madsrdf:Language .
  ?language madsrdf:code ?code .
  ?manifestation dc:language ?language .
}
GROUP BY ?language ?code
ORDER BY DESC(?count)
LIMIT 10
""")

st.code("""
# Fechas de publicación con más manifestaciones
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX rdam: <http://rdaregistry.info/Elements/m/>
SELECT ?year (COUNT(?manifestation) AS ?count) WHERE {
  ?date rdf:type time:Instant .
  ?manifestation rdam:dateOfPublication ?date .
  ?date time:inDateTime ?desc .
  ?desc time:year ?year .
}
GROUP BY ?year
ORDER BY DESC(?count)
LIMIT 10
""")
