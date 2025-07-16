import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("🔍 Buscar 'Oviedo' en BVMC vía JSON embebido")

def get_person_json_uri(texto):
    # Buscar la página HTML del autor con ID 360
    url = "https://data.cervantesvirtual.com/person/360"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    # Buscar enlace "Exportar: JSON"
    link = soup.find('a', string="JSON")
    return link["href"] if link else None

def load_person_json(json_uri):
    r = requests.get(json_uri)
    if r.status_code != 200:
        return None
    return r.json()

def extract_titles(person_data, max_titulos=10):
    roles = person_data.get("roles", [])
    for rol in roles:
        if rol.get("role") == "autor":
            obras = rol.get("works", [])[:max_titulos]
            return [w.get("title") for w in obras]
    return []

# 🛠️ Flujo de ejecución
st.info("Buscando autor que contenga 'Oviedo'…")
json_uri = get_person_json_uri("Oviedo")
if not json_uri:
    st.error("No se encontró la URL JSON de Gonzalo Fernández de Oviedo.")
else:
    st.success(f"URL JSON: {json_uri}")
    person = load_person_json(json_uri)
    if not person:
        st.error("No se pudo cargar el JSON desde la URL.")
    else:
        st.success(f"Autor: {person.get('name')}")
        titulos = extract_titles(person)
        if not titulos:
            st.warning("No se encontraron títulos en los roles de autor.")
        else:
            df = pd.DataFrame({"Título": titulos})
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_default_column(editable=False, sortable=True, filter=True)
            gb.configure_selection("single", use_checkbox=False)
            AgGrid(df, gridOptions=gb.build(),
                   update_mode=GridUpdateMode.NO_UPDATE,
                   height=300, theme="alpine")
