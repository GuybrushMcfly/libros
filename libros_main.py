import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock

# --- Configuración inicial ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Verificación de sesión activa ---
def verificar_sesion():
    if 'authentication_status' not in st.session_state:
        return False
    return st.session_state.get('authentication_status') == True

# --- Login de usuario ---
if not verificar_sesion():
    login_info = login()
    if not login_info:
        st.stop()  # Mostrar solo el formulario de login
    
    nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info
    
    if not autenticado:
        st.stop()
    
    if requiere_cambio:
        st.warning("⚠️ Debe cambiar su contraseña antes de continuar")
        st.stop()
    
    # Guardar estado de autenticación
    st.session_state.update({
        'auth_data': login_info,
        'authentication_status': True,
        'usuario': usuario,
        'nombre': nombre
    })
    st.rerun()  # Recargar para mostrar la aplicación

# --- Cerrar sesión ---
def cerrar_sesion():
    if 'auth_data' in st.session_state:
        _, _, _, authenticator, _, _ = st.session_state['auth_data']
        authenticator.logout('logout', 'main')
    st.session_state.clear()
    st.rerun()

# --- Interfaz principal ---
if verificar_sesion():
    # Obtener datos de sesión
    auth_data = st.session_state.get('auth_data')
    nombre = st.session_state.get('nombre')
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {nombre}")
        st.markdown("---")
        st.markdown("**🕒 Último acceso:**")
        st.markdown("Ahora mismo")
        st.markdown("---")
        
        if st.button("🚪 Cerrar sesión", use_container_width=True, type="primary"):
            cerrar_sesion()
        
        st.markdown("---")
        st.markdown("*Sistema v1.0*")

    # Navegación
    pages = {
        "📥 INGRESOS": [
            st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon="📖")
        ],
        "📦 STOCK": [
            st.Page(ver_stock.ver_stock, title="Ver stock", icon="📦")
        ]
    }
    
    st.navigation(pages, position="sidebar").run()
