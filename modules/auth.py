import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import datetime, bcrypt, re, os

TIEMPO_MAX_SESION_MIN = 10  # Tiempo máximo de sesión en minutos

# --- Conexión Supabase ---
@st.cache_resource
def init_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    return create_client(url, key)

# --- Validación de contraseña nueva ---
def contraseña_valida(pwd: str) -> bool:
    return len(pwd) >= 6 and re.search(r"\d", pwd)

# --- Cargar usuarios desde tabla 'acceso' ---
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

# --- Función de login principal ---
def login():
    ahora = datetime.datetime.now()

    # Cierre de sesión por inactividad
    if "last_activity" in st.session_state:
        minutos_inactivos = (ahora - st.session_state["last_activity"]).total_seconds() / 60
        if minutos_inactivos > TIEMPO_MAX_SESION_MIN:
            st.session_state.clear()
            st.warning("🔐 Sesión cerrada por inactividad.")
            st.stop()

    st.session_state["last_activity"] = ahora

    # Cargar usuarios válidos
    usuarios_validos = cargar_usuarios()
    if not usuarios_validos:
        st.error("❌ No se encontraron usuarios válidos.")
        st.stop()

    # Configuración para streamlit-authenticator
    credentials = {"usernames": usuarios_validos}
    authenticator = stauth.Authenticate(
        credentials,
        "app_libreria",             # cookie_name
        "clave_super_secreta",      # signature key
        0.02                        # duración de cookie en días (~30 min)
    )

    # --- Formulario de login ---
    with st.container():
        login_result = authenticator.login(
            location="main",
            fields={
                "Form name": "Iniciar sesión",
                "Username": "Usuario",
                "Password": "Contraseña",
                "Login": "Ingresar"
            }
        )

    # --- Validar resultado del login ---
    if not login_result or len(login_result) != 3:
        st.error("⚠️ Error inesperado en autenticación.")
        return None

    nombre, estado, usuario = login_result

    if estado is None:
        st.warning("🔐 Por favor, ingresá tus credenciales.")
        return None

    if estado is False:
        st.error("❌ Usuario o contraseña incorrectos.")
        return None

    # --- Usuario autenticado correctamente ---
    if estado is True:
        st.session_state["usuario"] = usuario
        st.session_state["nombre_completo"] = nombre

        supabase = init_connection()

        # Verificar si debe cambiar la contraseña
        datos = supabase.table("acceso")\
            .select("cambiar_password")\
            .eq("usuario", usuario).maybe_single().execute().data

        cambiar_password = datos["cambiar_password"] if datos else False

        # Registrar último acceso
        supabase.table("acceso").update({
            "ultimo_acceso": ahora.isoformat()
        }).eq("usuario", usuario).execute()

        return nombre, True, usuario, authenticator, supabase, cambiar_password
