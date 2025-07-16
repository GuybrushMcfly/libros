import streamlit as st
from streamlit import page  # Import necesario para @page

st.set_page_config(page_title="Librería", layout="wide")

# 🔹 Definimos páginas como funciones decoradas con @page
@page(title="Registrar libro", icon=":material/book:")
def registrar_libro():
    st.header("📘 Registrar libro")
    st.write("Aquí irá el formulario para registrar un nuevo libro.")

@page(title="Registrar editorial", icon=":material/business:", )
def registrar_editorial():
    st.header("🏢 Registrar editorial")
    st.write("Aquí irá el formulario para ingresar una nueva editorial (en el futuro).")

@page(title="Registrar proveedor", icon=":material/local_shipping:")
def registrar_proveedor():
    st.header("🚚 Registrar proveedor")
    st.write("Aquí irá el formulario para registrar un proveedor (en el futuro).")

@page(title="Buscar libro", icon=":material/search:")
def buscar_libro():
    st.header("🔍 Buscar libro")
    st.write("Aquí irá el buscador de libros.")

@page(title="Buscar editorial", icon=":material/business_center:")
def buscar_editorial():
    st.header("🏢 Buscar editorial")
    st.write("Aquí irá la búsqueda de editoriales.")

@page(title="Buscar proveedor", icon=":material/store_mall_directory:")
def buscar_proveedor():
    st.header("🚚 Buscar proveedor")
    st.write("Aquí irá la búsqueda de proveedores.")

# 🧭 Definimos el menú de navegación con secciones
pages = {
    "INGRESOS": [
        st.Page(registrar_libro),
        st.Page(registrar_editorial),
        st.Page(registrar_proveedor),
    ],
    "BUSQUEDA": [
        st.Page(buscar_libro),
        st.Page(buscar_editorial),
        st.Page(buscar_proveedor),
    ],
}

# 🔝 Creamos el menú superior y ejecutamos la página seleccionada
current_page = st.navigation(pages, position="top")
current_page.run()
