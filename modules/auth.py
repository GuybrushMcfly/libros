import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import datetime, bcrypt, re, os

TIEMPO_MAX_SESION_MIN = 10  # Logout automático tras 10 minutos

@st.cache_resource
def init_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    return create_client(url, key)

def contraseña_valida(pwd: str) -> bool:
    return len(pwd) >= 6 and re.search(r"\d", pwd) is not None

def hashear_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def login():
    ahora = datetime.datetime.now()
    supabase = init_connection()

    # --- Logout por inactividad ---
    if "last_activity" in st.session_state:
        minutos = (ahora - st.session_state["last_activity"]).total_seconds() / 60
        if minutos > TIEMPO_MAX_SESION_MIN:
            st.session_state.clear()
            st.warning("🔐 Sesión cerrada por inactividad.")
            if st.button("🔁 Volver al login"):
                st.rerun()
            st.stop()
    st.session_state["last_activity"] = ahora

    # --- Cargar usuarios activos desde tabla 'acceso' ---
    resultado = supabase.table("acceso")\
        .select("usuario, password, cambiar_password, activo")\
        .eq("activo", True).execute()

    usuarios = resultado.data
    if not usuarios:
        st.error("❌ No se encontraron usuarios activos.")
        st.stop()

    credentials = {
        "usernames": {}
    }
    for u in usuarios:
        usuario = u.get("usuario", "").strip().lower()
        password = u.get("password", "")
        if not usuario or not password or not password.startswith("$2b$"):
            continue
        credentials["usernames"][usuario] = {
            "name": usuario,
            "password": password,
            "email": f"{usuario}@ejemplo.com"
        }

    credentials = {
        "usernames": {...},
        "cookie": {
            "expiry_days": 0.007,
            "key": "clave_segura_app_libreria",
            "name": "libreria_sesion"
        }
    }
    
    authenticator = stauth.Authenticate(
        credentials=credentials["usernames"],
        cookie_name=credentials["cookie"]["name"],
        key=credentials["cookie"]["key"],
        cookie_expiry_days=credentials["cookie"]["expiry_days"]
    )


    # --- Login ---
    try:
        nombre, estado, usuario = authenticator.login("Iniciar sesión")
    except Exception as e:
        st.error(f"❌ Error en el login: {e}")
        st.stop()

    # --- Evaluar estado ---
    if estado is None:
        st.warning("🔐 Por favor, ingresá tus credenciales.")
        return None

    if estado is False:
        st.error("❌ Usuario o contraseña incorrectos.")
        return None

    if estado is True:
        if usuario not in credentials["usernames"]:
            st.error("❌ Usuario inválido.")
            authenticator.logout("Reintentar", "main")
            st.stop()

        st.session_state["usuario"] = usuario
        st.session_state["nombre_completo"] = nombre

        datos = supabase.table("acceso")\
            .select("cambiar_password")\
            .eq("usuario", usuario).maybe_single().execute().data
        cambiar_password = datos["cambiar_password"] if datos else False

        supabase.table("acceso").update({
            "ultimo_acceso": ahora.isoformat()
        }).eq("usuario", usuario).execute()

        return nombre, estado, usuario, authenticator, supabase, cambiar_password
