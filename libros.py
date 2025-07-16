import streamlit as st

st.set_page_config(page_title="Librería", layout="wide")

pages = {
    "INGRESOS": ["Registrar libro", "Registrar editorial", "Registrar proveedor"],
    "BUSQUEDA": ["Buscar libro", "Buscar editorial", "Buscar proveedor"],
    "VENTAS": ["opcion1", "opcion2"],
    "STOCK": ["opcion1", "opcion2"],
    "PEDIDOS": ["opcion1", "opcion2"],
}

pg = st.navigation(pages, position="top")
pg.run()
