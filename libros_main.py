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
if autenticado is False:
    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()
elif autenticado is None:
    st.info("🔐 Por favor ingresá tus credenciales.")
    st.stop()
elif requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Función para cerrar sesión ---
def cerrar_sesion():
    st.session_state.clear()
    st.success("🔓 Sesión cerrada exitosamente")
    st.rerun()

# --- Sidebar con información del usuario ---
with st.sidebar:
    st.markdown(f"### 👤 {nombre}")
    st.markdown("---")
    st.markdown("**🕒 Último acceso:**")
    st.markdown("*Hoy, 10:30 AM*")
    st.markdown("---")
    
    if st.button("🚪 Cerrar sesión", use_container_width=True, type="secondary"):
        cerrar_sesion()
    
    st.markdown("---")
    st.markdown("*Gestión Librería v1.0*")

# --- Menú de navegación principal en sidebar ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon=":material/library_add:")
    ],
    "📦 STOCK": [
        st.Page(ver_stock.ver_stock, title="Ver stock", icon=":material/inventory_2:")
    ]
}

# --- Ejecutar navegación en sidebar ---
pg = st.navigation(pages, position="sidebar")
pg.run()
