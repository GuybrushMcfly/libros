import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("🔍 Buscar autor y títulos en BVMC (scraping)")

def buscar_autor_uri(texto):
    url = f"https://www.cervantesvirtual.com/search/?q={texto}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    enlace = soup.select_one("a[href*='/person/']")
    return enlace["href"] if enlace else None

def obtener_titulos_de_autor(uri_autor, max_titulos=10):
    url = f"https://www.cervantesvirtual.com{uri_autor}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    titulos = [
        tag.get_text(strip=True)
        for tag in soup.select("ul.obras li a")
    ][:max_titulos]
    return titulos

nombre = st.text_input("Ingresa el nombre del autor (ej. Oviedo)")
if st.button("Buscar títulos"):
    if not nombre.strip():
        st.warning("Por favor ingresa un nombre.")
    else:
        uri = buscar_autor_uri(nombre)
        if not uri:
            st.error(f"No se encontró ningún autor relacionado con '{nombre}'.")
        else:
            st.success(f"Autor encontrado: {uri}")
            titulos = obtener_titulos_de_autor(uri)
            if not titulos:
                st.warning("El autor no tiene títulos listados o la estructura cambió.")
            else:
                df = pd.DataFrame({"Título": titulos})
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_default_column(editable=False, sortable=True, filter=True)
                gb.configure_selection("single", use_checkbox=False)
                grid = gb.build()
                AgGrid(df, gridOptions=grid, update_mode=GridUpdateMode.NO_UPDATE,
                       height=300, theme="alpine")
