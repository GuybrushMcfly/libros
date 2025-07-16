import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("🔍 Buscar 'Oviedo' en BVMC vía JSON")

def buscar_autor_json(texto):
    # Llamada a la API JSON de personas
    r = requests.get("https://data.cervantesvirtual.com/person/360.json")
    if r.status_code != 200:
        return None
    data = r.json()
    # Verificar si coincide el nombre
    nombre = data.get("name", "").lower()
    if texto.lower() in nombre:
        return data
    return None

def extraer_titulos_autor(data, max_titulos=10):
    roles = data.get("roles", [])
    for rol in roles:
        if rol.get("role") == "autor":
            obras = rol.get("works", [])[:max_titulos]
            return [w.get("title") for w in obras]
    return []

# Buscás "Oviedo"
autor_data = buscar_autor_json("Oviedo")
if not autor_data:
    st.error("No se encontró 'Oviedo' en los datos JSON de BVMC.")
else:
    st.success(f"Autor: {autor_data.get('name')}")
    titulos = extraer_titulos_autor(autor_data)
    if not titulos:
        st.warning("No se encontraron títulos para este autor.")
    else:
        df = pd.DataFrame({"Título": titulos})
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=False, sortable=True, filter=True)
        gb.configure_selection("single", use_checkbox=False)
        AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.NO_UPDATE,
               height=300, theme="alpine")
