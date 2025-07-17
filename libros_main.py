import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock  # y otros que vayas creando

# --- Configuración inicial ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Login de usuario ---
login_info = login()
if not login_info:
    st.stop()

nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info

# --- Controles post-login ---
if not autenticado or "usuario" not in st.session_state:
    st.warning("🔒 Debés iniciar sesión para acceder.")
    st.stop()

if requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Función para cerrar sesión como página ---
def cerrar_sesion():
    st.session_state.clear()
    st.markdown("""
        <meta http-equiv="refresh" content="0; url=/" />
        <p>🔓 Cerrando sesión...</p>
    """, unsafe_allow_html=True)
    st.stop()

# --- Menú de navegación principal ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon=":material/library_add:"),
    ],
    "📦 STOCK": [
        st.Page(ver_stock.ver_stock, title="Ver stock", icon=":material/inventory_2:"),
    ],
    "🔓 SESIÓN": [
        st.Page(cerrar_sesion, title="Cerrar sesión", icon=":material/logout:")
    ]
}

# --- Mostrar nombre de usuario arriba a la izquierda (opcional) ---
st.markdown(f"<div style='text-align: right; font-size: 14px;'>👤 {nombre}</div>", unsafe_allow_html=True)

# --- Ejecutar navegación ---
pg = st.navigation(pages, position="top")
pg.run()
