import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

ENDPOINT = "http://data.cervantesvirtual.com/bvmc-lod/repositories/data"

def obtener_manifestaciones(persona_uri, limite=10):
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

st.title("📚 Obras del autor desde BVMC (SPARQL)")

# Selector de autor con URI
autores = {
    "Miguel de Cervantes Saavedra": "http://data.cervantesvirtual.com/person/40",
    "Gonzalo Fernández de Oviedo y Valdés": "http://data.cervantesvirtual.com/person/360"
}
nombre = st.selectbox("Selecciona un autor:", list(autores.keys()))
uri = autores[nombre]

if st.button("Mostrar obras"):
    obras = obtener_manifestaciones(uri, limite=20)
    if obras:
        df = pd.DataFrame(obras, columns=["Manifestación (URI)", "Título"])
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(sortable=True, filter=True)
        gb.configure_selection("single", use_checkbox=False)
        AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.NO_UPDATE, height=400, theme="alpine")
    else:
        st.warning("No se encontraron obras para este autor.")
