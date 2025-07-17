import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock

# --- Configuración inicial ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Login de usuario ---
login_info = login()

# Validar que devolvió datos completos
if not login_info or not isinstance(login_info, tuple) or len(login_info) != 6:
    st.stop()

nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info

# Controles estrictos post-login
if not autenticado or "usuario" not in st.session_state:
    st.stop()  # Ya mostramos los mensajes en el módulo de login

if requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Función para cerrar sesión ---
def cerrar_sesion():
    authenticator.logout('Cerrar sesión', 'main')
    st.session_state.clear()
    st.rerun()

# --- Solo mostrar la sidebar y navegación si el usuario está autenticado ---
if autenticado:
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

    # --- Menú de navegación principal ---
    pages = {
        "📥 INGRESOS": [
            st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon="📖")
        ],
        "📦 STOCK": [
            st.Page(ver_stock.ver_stock, title="Ver stock", icon="📦")
        ]
    }
    
    # Mostrar navegación solo cuando está autenticado
    pg = st.navigation(pages, position="sidebar")
    pg.run()
