import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("🔍 Obras de Oviedo desde BVMC vía JSON‑LD")

def cargar_jsonld_autor(id_autor=360):
    url = (
        "https://data.cervantesvirtual.com/getRDF"
        "?uri=http://data.cervantesvirtual.com/person/360"
        "&format=jsonld"
    )
    r = requests.get(url)
    if r.status_code != 200:
        st.error(f"Error al solicitar datos JSON‑LD: {r.status_code}")
        return None
    try:
        return r.json()
    except ValueError:
        st.error("No se pudo decodificar JSON‑LD")
        return None

def extraer_titulos_jsonld(js):
    titles = set()
    for obj in js:
        # Extraemos cualquier predicado dct:title
        titulo = obj.get("http://purl.org/dc/terms/title")
        if titulo:
            if isinstance(titulo, list):
                for t in titulo:
                    if "@value" in t:
                        titles.add(t["@value"])
            elif isinstance(titulo, str):
                titles.add(titulo)
    return list(titles)[:10]

# Procesar datos de Oviedo
js = cargar_jsonld_autor()
if not js:
    st.stop()

titulos = extraer_titulos_jsonld(js)
if not titulos:
    st.warning("No se encontraron títulos en los datos JSON‑LD.")
else:
    df = pd.DataFrame({"Título": titulos})
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(sortable=True, filter=True, editable=False)
    gb.configure_selection("single", use_checkbox=False)
    grid_opts = gb.build()
    AgGrid(df, gridOptions=grid_opts, update_mode=GridUpdateMode.NO_UPDATE,
           height=300, theme="alpine")
