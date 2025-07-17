import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock
import time

# --- Configuración inicial ---
st.set_page_config(
    layout="wide",
    page_title="Gestión Librería",
    page_icon="📚",
    initial_sidebar_state="collapsed"  # Sidebar oculta inicialmente
)

# --- Variables de sesión necesarias ---
required_session_keys = [
    'authentication_status',
    'usuario',
    'nombre',
    'auth_data',
    'last_activity'
]

# --- Función para verificar sesión válida ---
def sesion_valida():
    # Verificar que todas las claves requeridas existan
    if not all(key in st.session_state for key in required_session_keys):
        return False
    
    # Verificar tiempo de inactividad (10 minutos máximo)
    tiempo_inactivo = time.time() - st.session_state.get('last_activity', 0)
    if tiempo_inactivo > 600:  # 10 minutos en segundos
        st.session_state.clear()
        st.warning("Sesión expirada por inactividad")
        return False
    
    return st.session_state['authentication_status']

# --- Función para actualizar actividad ---
def actualizar_actividad():
    st.session_state['last_activity'] = time.time()

# --- Función para cerrar sesión ---
def cerrar_sesion():
    # Ejecutar logout del authenticator si existe
    if 'auth_data' in st.session_state:
        try:
            _, _, _, authenticator, _, _ = st.session_state['auth_data']
            authenticator.logout('logout', 'main')
        except Exception as e:
            st.error(f"Error al cerrar sesión: {str(e)}")
    
    # Limpiar completamente la sesión
    st.session_state.clear()
    st.rerun()

# --- Página de Login ---
def mostrar_login():
    st.title("📚 Gestión de Librería")
    st.markdown("---")
    
    with st.container():
        login_info = login()
        
        if login_info and len(login_info) == 6:
            nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info
            
            if autenticado:
                if requiere_cambio:
                    st.warning("⚠️ Debes cambiar tu contraseña antes de continuar")
                    st.stop()
                
                # Establecer datos de sesión
                st.session_state.update({
                    'authentication_status': True,
                    'usuario': usuario,
                    'nombre': nombre,
                    'auth_data': login_info,
                    'last_activity': time.time()
                })
                st.rerun()

# --- Página Principal ---
def mostrar_aplicacion():
    # Actualizar tiempo de actividad
    actualizar_actividad()
    
    # Obtener datos del usuario
    nombre = st.session_state.get('nombre', 'Usuario')
    auth_data = st.session_state.get('auth_data')
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {nombre}")
        st.markdown("---")
        
        # Mostrar tiempo de inactividad
        tiempo_inactivo = time.time() - st.session_state['last_activity']
        minutos_inactivo = int(tiempo_inactivo // 60)
        st.markdown(f"**🕒 Inactividad:** {minutos_inactivo} min")
        st.markdown("---")
        
        # Botón de cerrar sesión
        if st.button(
            "🚪 Cerrar sesión",
            use_container_width=True,
            type="primary",
            key="logout_btn"
        ):
            cerrar_sesion()
        
        st.markdown("---")
        st.markdown("*Sistema v2.0*")

    # Navegación y páginas
    pages = {
        "📥 INGRESOS": [
            st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon="📖")
        ],
        "📦 STOCK": [
            st.Page(ver_stock.ver_stock, title="Ver stock", icon="📦")
        ]
    }
    
    st.navigation(pages, position="sidebar").run()

# --- Flujo principal de la aplicación ---
if not sesion_valida():
    mostrar_login()
    st.stop()  # Detener ejecución si no está autenticado
else:
    mostrar_aplicacion()
