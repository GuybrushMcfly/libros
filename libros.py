import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

ENDPOINT = "http://data.cervantesvirtual.com/bvmc-lod/repositories/data"

def obras_autor_bvmc(uri_autor, limite=10):
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(f"""
        PREFIX rdac: <http://rdaregistry.info/Elements/c/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?rol ?m ?label
        WHERE {{
            <{uri_autor}> ?rol ?m .
            ?m a rdac:Manifestation .
            ?m rdfs:label ?label .
        }}
        LIMIT {limite}
    """)
    sparql.setReturnFormat(JSON)
    result = sparql.queryAndConvert()
    return [{
        "Título": b["label"]["value"],
        "Manifestación": b["m"]["value"],
        "Rol": b["rol"]["value"]
    } for b in result["results"]["bindings"]]

st.title("📚 Obras desde BVMC usando SPARQL oficial")

opciones = {
    "Miguel de Cervantes Saavedra": "http://data.cervantesvirtual.com/person/40",
    "Gonzalo Fernández de Oviedo y Valdés": "http://data.cervantesvirtual.com/person/360"
}
autor = st.selectbox("Seleccionar autor", list(opciones.keys()))
uri_autor = opciones[autor]

if st.button("Mostrar obras"):
    datos = obras_autor_bvmc(uri_autor)
    if datos:
        df = pd.DataFrame(datos)
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(filter=True, sortable=True)
        gb.configure_selection("single", use_checkbox=False)
        AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.NO_UPDATE,
               height=400, theme="alpine")
    else:
        st.warning("⚠️ No se encontraron datos para este autor.")
