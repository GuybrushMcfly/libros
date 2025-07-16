import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("🔍 Buscar 'Oviedo' en BVMC vía JSON-LD")

def obtener_datos_autor(id_autor):
    url = (
        "https://data.cervantesvirtual.com/getRDF"
        "?uri=http://data.cervantesvirtual.com/person/360"
        "&format=jsonld"
    )
    r = requests.get(url)
    if r.status_code != 200:
        st.error("Error al llamar a la API JSON-LD")
        return None
    try:
        return r.json()
    except Exception:
        st.error("No se pudo parsear JSON desde JSON-LD")
        return None

def extraer_titulos(data, max_titulos=10):
    # JSON-LD viene con estructura lista de objetos
    for obj in data:
        if obj.get("@id", "").endswith("/person/360"):
            works = obj.get("http://purl.org/dc/terms/creator", [])
            # alternativamente buscar predicados relacionados a obras
            break
    # No es estándar: vamos a extraer todos los títulos que aparezcan
    titulos = []
    for obj in data:
        title = obj.get("http://purl.org/dc/terms/title")
        if title:
            if isinstance(title, list):
                titulos.extend([t.get("@value") for t in title if "@value" in t])
            elif isinstance(title, str):
                titulos.append(title)
    return titulos[:max_titulos]

data = obtener_datos_autor(360)
if data:
    titulos = extraer_titulos(data)
    if not titulos:
        st.warning("No se encontró ningún título en los datos JSON-LD.")
    else:
        df = pd.DataFrame({"Título": titulos})
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(sortable=True, filter=True, editable=False)
        gb.configure_selection("single", use_checkbox=False)
        AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.NO_UPDATE,
               height=300, theme="alpine")
