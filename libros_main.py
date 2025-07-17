import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock

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

# --- Header con usuario y botón de logout ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<div style='font-size: 14px; padding-top: 10px;'>👤 {nombre}</div>", unsafe_allow_html=True)
with col2:
    if st.button("🔓 Cerrar sesión", type="secondary"):
        st.session_state.clear()
        st.success("🔓 Sesión cerrada exitosamente")
        st.rerun()

st.markdown("---")  # Separador visual

# --- Menú de navegación principal (SIN logout) ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon=":material/library_add:"),
    ],
    "📦 STOCK": [
        st.Page(ver_stock.ver_stock, title="Ver stock", icon=":material/inventory_2:"),
    ]
}

# --- Ejecutar navegación ---
pg = st.navigation(pages, position="top")
pg.run()
