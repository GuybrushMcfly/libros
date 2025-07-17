import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import datetime, bcrypt, re, os

TIEMPO_MAX_SESION_MIN = 10

@st.cache_resource
def init_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    return create_client(url, key)

def contraseña_valida(pwd: str) -> bool:
    return len(pwd) >= 6 and re.search(r"\d", pwd)

def cargar_usuarios():
    supabase = init_connection()
    resultado = supabase.table("acceso")\
        .select("usuario, password, activo, cambiar_password")\
        .eq("activo", True).execute()

    usuarios = {}
    for u in resultado.data:
        user = u["usuario"].strip().lower()
        password = u["password"]
        if not user or not password or not password.startswith("$2b$"):
            continue
        usuarios[user] = {
            "name": user,
            "password": password,
            "email": f"{user}@ejemplo.com"
        }
    return usuarios

def login():
    ahora = datetime.datetime.now()
    if "last_activity" in st.session_state:
        if (ahora - st.session_state["last_activity"]).total_seconds() > TIEMPO_MAX_SESION_MIN * 60:
            st.session_state.clear()
            st.warning("🔐 Sesión cerrada por inactividad.")
            st.stop()
    st.session_state["last_activity"] = ahora

    usuarios_validos = cargar_usuarios()

    if not usuarios_validos:
        st.error("❌ No se encontraron usuarios válidos.")
        st.stop()

    credentials = {
        "usernames": usuarios_validos
    }

    authenticator = stauth.Authenticate(
        credentials,
        "app_libreria",              # cookie_name
        "clave_super_secreta",       # cookie_key
        0.02                         # cookie_expiry_days
    )

    nombre, estado, usuario = authenticator.login()

    if estado is False:
        st.error("❌ Usuario o contraseña incorrectos.")
        return None
    elif estado is None:
        st.warning("🔐 Por favor, ingresá tus credenciales.")
        return None

    st.session_state["usuario"] = usuario
    st.session_state["nombre_completo"] = usuario
    supabase = init_connection()

    # Obtener si debe cambiar contraseña
    datos = supabase.table("acceso")\
        .select("cambiar_password")\
        .eq("usuario", usuario).maybe_single().execute().data

    cambiar_password = datos["cambiar_password"] if datos else False

    # Registrar último acceso
    supabase.table("acceso").update({
        "ultimo_acceso": ahora.isoformat()
    }).eq("usuario", usuario).execute()

    return nombre, True, usuario, authenticator, supabase, cambiar_password
