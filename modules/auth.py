import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import datetime, os

# Configuración
TIEMPO_MAX_SESION_MIN = 10
COOKIE_EXPIRY_DAYS = 1/720  # 2 minutos en días (para testing)

def init_connection():
    return create_client(os.environ.get("SUPABASE_URL"), 
                       os.environ.get("SUPABASE_SERVICE_KEY"))

def cargar_usuarios():
    supabase = init_connection()
    resultado = supabase.table("acceso")\
              .select("usuario, password, activo, cambiar_password")\
              .eq("activo", True).execute()
    
    return {u["usuario"].strip().lower(): {
        "name": u["usuario"],
        "password": u["password"],
        "email": f"{u['usuario']}@ejemplo.com"
    } for u in resultado.data if u["password"].startswith("$2b$")}

def login():
    # Resetear estado de autenticación al inicio
    if 'authentication_status' in st.session_state:
        del st.session_state['authentication_status']
    
    # Cargar usuarios
    usuarios_validos = cargar_usuarios()
    if not usuarios_validos:
        st.error("❌ No hay usuarios configurados")
        st.stop()

    # Configurar autenticador
    authenticator = stauth.Authenticate(
        {"usernames": usuarios_validos},
        "libreria_auth",
        os.environ.get("AUTH_SECRET_KEY"),
        COOKIE_EXPIRY_DAYS,
        preauthorized=False
    )

    # Mostrar formulario de login
    login_container = st.empty()
    with login_container.container():
        nombre, estado, username = authenticator.login("Acceso al Sistema", "main")

    # Manejar estados de autenticación
    if estado is None:
        st.warning("🔐 Ingrese sus credenciales")
        return None
    
    if estado is False:
        st.error("❌ Credenciales incorrectas")
        login_container.empty()  # Limpiar el formulario
        return None

    if estado is True:
        # Registrar acceso
        supabase = init_connection()
        supabase.table("acceso").update({
            "ultimo_acceso": datetime.datetime.now().isoformat()
        }).eq("usuario", username).execute()

        # Obtener si requiere cambio de contraseña
        user_data = supabase.table("acceso")\
                     .select("cambiar_password")\
                     .eq("usuario", username)\
                     .maybe_single().execute().data

        return (nombre, True, username, authenticator, 
                supabase, user_data.get("cambiar_password", False))
