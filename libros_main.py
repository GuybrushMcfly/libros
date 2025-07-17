import streamlit as st
from modules.auth import login
from views import (
    registrar_libro,
    ver_stock,

)

# --- Configuración general ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Login ---
login_info = login()

if not login_info:
    st.stop()

nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info

if not autenticado:
    st.stop()

if requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Menú principal ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro, title="Registrar libro", icon=":material/library_add:"),
        st.Page(registrar_editorial, title="Registrar editorial", icon=":material/edit:"),
        st.Page(registrar_proveedor, title="Registrar proveedor", icon=":material/business:"),
        st.Page(registrar_autor, title="Registrar autor", icon=":material/person_add:"),
    ],
    "🔍 BÚSQUEDA": [
        st.Page(buscar_libros, title="Buscar libros", icon=":material/search:"),
        st.Page(buscar_ventas, title="Buscar ventas", icon=":material/receipt_long:"),
    ],
    "💸 VENTAS": [
        st.Page(registrar_venta, title="Registrar venta", icon=":material/point_of_sale:"),
        st.Page(historial_ventas, title="Historial de ventas", icon=":material/history:"),
    ],
    "📦 STOCK": [
        st.Page(ver_stock, title="Ver stock", icon=":material/inventory_2:"),
        st.Page(actualizar_stock, title="Actualizar stock", icon=":material/update:"),
    ],
    "📑 PEDIDOS": [
        st.Page(registrar_pedido, title="Registrar pedido", icon=":material/post_add:"),
        st.Page(historial_pedidos, title="Historial de pedidos", icon=":material/list_alt:"),
    ]
}

# --- Ejecutar navegación ---
pg = st.navigation(pages, position="top")
pg.run()
