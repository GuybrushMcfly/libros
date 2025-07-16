import streamlit as st

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Librería", page_icon="📚")

# --- Páginas simuladas ---
def registrar_libro():
    st.title("📘 Registrar libro")
    st.write("Formulario para registrar un nuevo libro.")

def registrar_venta():
    st.title("💰 Registrar venta")
    st.write("Formulario para registrar una venta.")

def ver_stock():
    st.title("📦 Ver stock")
    st.write("Listado y control de stock de libros.")

# --- Definir secciones del menú ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro, title="Registrar libro", icon=":material/library_add:"),
    ],
    "💸 VENTAS": [
        st.Page(registrar_venta, title="Registrar venta", icon=":material/point_of_sale:"),
    ],
    "📦 STOCK": [
        st.Page(ver_stock, title="Ver stock", icon=":material/inventory:"),
    ]
}

# --- Activar navegación superior ---
pg = st.navigation(pages, position="top")
pg.run()
