import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import datetime, bcrypt, re, os

@st.cache_resource
def init_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    return create_client(url, key)

def contraseña_valida(pwd: str) -> bool:
    return len(pwd) >= 6 and re.search(r"\d", pwd)

def cargar_usuarios():
    supabase = init_connection()
    result = supabase.table("usuarios")\
        .select("usuario, password, apellido_nombre, activo, cambiar_password")\
        .eq("activo", True).execute()

    credenciales = {"usernames": {}}
    for u in result.data:
        user = u["usuario"].strip().lower()
        if not user or not u["password"].startswith("$2b$"):
            continue
        credenciales["usernames"][user] = {
            "name": u["apellido_nombre"],
            "password": u["password"],
            "email": f"{user}@ejemplo.com"
        }
    return credenciales

def login():
    # Logout automático
    ahora = datetime.datetime.now()
    if "last_activity" in st.session_state:
        if (ahora - st.session_state["last_activity"]).total_seconds() > 600:
            st.session_state.clear()
            st.warning("Sesión cerrada por inactividad.")
            st.stop()
    st.session_state["last_activity"] = ahora

    credenciales = cargar_usuarios()

    authenticator = stauth.Authenticate(
        credentials={"usernames": credenciales["usernames"]},
        cookie_name="libros_app",
        cookie_key="clave_segura_libros",
        cookie_expiry_days=0.02
    )

    nombre, estado, usuario = authenticator.login()

    if estado:
        st.session_state["usuario"] = usuario
        st.session_state["nombre_completo"] = credenciales["usernames"][usuario]["name"]
        supabase = init_connection()
        datos = supabase.table("usuarios").select("cambiar_password").eq("usuario", usuario).maybe_single().execute().data
        necesita_cambio = datos["cambiar_password"] if datos else False
        return nombre, True, usuario, authenticator, supabase, necesita_cambio

    return None, estado, usuario, authenticator, None, False
