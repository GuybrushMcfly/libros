import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

# Configuración del endpoint SPARQL de la BVMC
ENDPOINT = "http://data.cervantesvirtual.com/bvmc-lod/repositories/data"

@st.cache_data(show_spinner=False)
def buscar_autores(nombre, limite=20):
    sparql = SPARQLWrapper(ENDPOINT)
    q = f"""
      PREFIX foaf: <http://xmlns.com/foaf/0.1/>
      SELECT DISTINCT ?autor ?name WHERE {{
        ?autor a foaf:Person ;
               foaf:name ?name .
        FILTER(CONTAINS(LCASE(?name), LCASE("{nombre}")))
      }} LIMIT {limite}
    """
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    res = sparql.queryAndConvert()
    return [(r["autor"]["value"], r["name"]["value"]) for r in res["results"]["bindings"]]

@st.cache_data(show_spinner=False)
def obtener_titulos_de_autor(uri_autor, limite=10):
    sparql = SPARQLWrapper(ENDPOINT)
    q = f"""
      PREFIX dct: <http://purl.org/dc/terms/>
      SELECT DISTINCT ?work ?title WHERE {{
        ?work dct:creator <{uri_autor}> ;
              dct:title ?title .
      }} LIMIT {limite}
    """
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    res = sparql.queryAndConvert()
    return [(r["work"]["value"], r["title"]["value"]) for r in res["results"]["bindings"]]

st.title("📖 Buscador bilingüe de autores y títulos (BVMC)")

nombre = st.text_input("Escribe parte del nombre del autor:")
if st.button("Buscar autores"):
    if nombre.strip():
        autores = buscar_autores(nombre)
        if autores:
            uri_sel, nombre_sel = st.selectbox(
                "Seleccioná un autor:",
                opciones=autores,
                format_func=lambda x: x[1]
            )
            if st.button("Buscar títulos"):
                titulos = obtener_titulos_de_autor(uri_sel)
                if titulos:
                    df = pd.DataFrame(titulos, columns=["Work URI", "Título"])
                    st.dataframe(df)
                else:
                    st.warning("No se encontraron títulos para ese autor.")
        else:
            st.warning("No se encontraron autores con ese nombre.")
