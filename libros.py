import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Endpoint SPARQL correcto
ENDPOINT = "http://data.cervantesvirtual.com/openrdf-sesame/repositories/data"

@st.cache_data
def busca_autores(parte):
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(f"""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT DISTINCT ?autor ?name WHERE {{
          ?autor a foaf:Person ;
                 foaf:name ?name .
          FILTER(CONTAINS(LCASE(?name), LCASE("{parte}")))
        }} LIMIT 10
    """)
    sparql.setReturnFormat(JSON)
    res = sparql.queryAndConvert()
    return [(b["autor"]["value"], b["name"]["value"]) for b in res["results"]["bindings"]]

@st.cache_data
def busca_titulos(uri_autor):
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(f"""
        PREFIX dct: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?title WHERE {{
          ?work dct:creator <{uri_autor}> ;
                dct:title ?title .
        }} LIMIT 10
    """)
    sparql.setReturnFormat(JSON)
    res = sparql.queryAndConvert()
    return [r["title"]["value"] for r in res["results"]["bindings"]]

st.title("🔍 Buscar ‘Oviedo’ en BVMC y listar títulos")

autores = busca_autores("Oviedo")
if not autores:
    st.error("No se encontró ningún autor con 'Oviedo'")
else:
    uri_sel, nombre_sel = st.selectbox("Seleccioná un autor:", autores, format_func=lambda x: x[1])
    if st.button("Mostrar títulos"):
        titulos = busca_titulos(uri_sel)
        if titulos:
            df = pd.DataFrame({"Título": titulos})
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_default_column(editable=False)
            gb.configure_selection("single", use_checkbox=False)
            gridOps = gb.build()
            AgGrid(df, gridOptions=gridOps, update_mode=GridUpdateMode.NO_UPDATE, height=300, theme="alpine")
        else:
            st.warning("Este autor no tiene títulos registrados.")
