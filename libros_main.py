import streamlit as st
from modules.auth import login

# Configuración inicial
st.set_page_config(
    layout="wide",
    page_title="Gestión Librería",
    page_icon="📚",
    initial_sidebar_state="collapsed"  # Sidebar inicialmente oculta
)

# Función para verificar estado de autenticación
def usuario_autenticado():
    return st.session_state.get('authentication_status', False)

# Mostrar login si no está autenticado
if not usuario_autenticado():
    st.title("Sistema de Gestión Librería")
    
    login_info = login()
    
    if login_info and len(login_info) == 6:
        nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info
        
        if autenticado:
            if requiere_cambio:
                st.warning("Debe cambiar su contraseña antes de continuar")
                st.stop()
            
            # Guardar estado de autenticación
            st.session_state.update({
                'authentication_status': True,
                'usuario': usuario,
                'nombre': nombre,
                'auth_data': login_info
            })
            st.rerun()  # Forzar recarga para mostrar la aplicación

    st.stop()  # Detener ejecución si no está autenticado

# Función para cerrar sesión
def cerrar_sesion():
    auth_data = st.session_state.get('auth_data')
    if auth_data:
        try:
            _, _, _, authenticator, _, _ = auth_data
            authenticator.logout('logout', 'main')
        except:
            pass
    
    st.session_state.clear()
    st.experimental_rerun()

# Interfaz principal (solo para autenticados)
if usuario_autenticado():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('nombre', 'Usuario')}")
        st.markdown("---")
        
        if st.button("🚪 Cerrar sesión", key="logout_btn", use_container_width=True):
            cerrar_sesion()
        
        st.markdown("---")
        st.markdown("*Sistema v1.0*")

    # Aquí iría tu navegación y páginas principales
    st.success(f"Bienvenido {st.session_state.get('nombre', 'Usuario')}!")
    # ... resto de tu lógica de la aplicación

else:
    st.warning("Por favor inicie sesión")
    st.stop()
