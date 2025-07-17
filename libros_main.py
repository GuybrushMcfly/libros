import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock

# --- Configuración inicial ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚", initial_sidebar_state="expanded")

# --- Login de usuario ---
login_info = login()
if not login_info or not isinstance(login_info, tuple) or len(login_info) != 6:
    st.stop()

nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info

# --- Validaciones de sesión ---
if not autenticado or "usuario" not in st.session_state:
    st.warning("🔒 Debés iniciar sesión para acceder.")
    st.stop()

if requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Función para cerrar sesión ---
def cerrar_sesion():
    st.session_state.clear()
    st.rerun()

# --- Sidebar personalizado ---
st.sidebar.image("logo-cap.png", use_container_width=True)
st.sidebar.markdown(f"**👤 {nombre}**")
st.sidebar.markdown("---")

# --- Menú de navegación lateral con texto descriptivo ---
st.sidebar.markdown("### 📥 Gestión de Ingresos")
if st.sidebar.button("📘 Registrar libro", use_container_width=True):
    st.session_state["pagina"] = "registrar_libro"

st.sidebar.markdown("### 📦 Control de Stock")
if st.sidebar.button("📦 Ver stock", use_container_width=True):
    st.session_state["pagina"] = "ver_stock"

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Cerrar sesión", use_container_width=True, type="secondary"):
    cerrar_sesion()

st.sidebar.markdown("📚 *Gestión Librería v1.0*")

# --- Renderizar la vista seleccionada ---
pagina = st.session_state.get("pagina", "registrar_libro")

if pagina == "registrar_libro":
    registrar_libro.registrar_libro()
elif pagina == "ver_stock":
    ver_stock.ver_stock()
else:
    st.info("Seleccioná una opción del menú lateral.")
