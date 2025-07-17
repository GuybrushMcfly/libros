import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import datetime, os

# Configuración
TIEMPO_MAX_SESION_MIN = 10
COOKIE_EXPIRY_DAYS = 0.002  # ~3 minutos para testing

def init_connection():
    return create_client(os.environ.get("SUPABASE_URL"), 
                       os.environ.get("SUPABASE_SERVICE_KEY"))

def cargar_usuarios():
    try:
        supabase = init_connection()
        resultado = supabase.table("acceso")\
                  .select("usuario, password, activo, cambiar_password")\
                  .eq("activo", True).execute()
        
        if not resultado.data:
            st.error("No se encontraron usuarios activos")
            return {}
            
        return {
            u["usuario"].strip().lower(): {
                "name": u["usuario"],
                "password": u["password"],
                "email": f"{u['usuario']}@ejemplo.com"
            } 
            for u in resultado.data 
            if u.get("password", "").startswith("$2b$")
        }
    except Exception as e:
        st.error(f"Error al cargar usuarios: {str(e)}")
        return {}

def login():
    # Estado inicial limpio
    if 'auth_initialized' not in st.session_state:
        st.session_state.clear()
        st.session_state['auth_initialized'] = True
    
    usuarios_validos = cargar_usuarios()
    if not usuarios_validos:
        st.stop()

    authenticator = stauth.Authenticate(
        {"usernames": usuarios_validos},
        "libreria_auth",
        os.environ.get("AUTH_SECRET_KEY", "default_secret_key"),
        COOKIE_EXPIRY_DAYS,
        preauthorized=False
    )

    # Contenedor para el formulario de login
    login_container = st.empty()
    
    with login_container.container():
        st.markdown("## Inicio de Sesión")
        nombre, estado, username = authenticator.login("Login", "main")

    # Manejo de estados
    if estado is False:
        st.error("Usuario o contraseña incorrectos")
        login_container.empty()
        return None
    
    if estado is True:
        try:
            supabase = init_connection()
            # Actualizar último acceso
            supabase.table("acceso").update({
                "ultimo_acceso": datetime.datetime.now().isoformat()
            }).eq("usuario", username).execute()
            
            # Verificar si requiere cambio de contraseña
            user_data = supabase.table("acceso")\
                         .select("cambiar_password")\
                         .eq("usuario", username)\
                         .maybe_single().execute().data
            
            return (
                nombre, 
                True, 
                username, 
                authenticator, 
                supabase, 
                user_data.get("cambiar_password", False) if user_data else False
            )
        except Exception as e:
            st.error(f"Error al autenticar: {str(e)}")
            return None
    
    return None
