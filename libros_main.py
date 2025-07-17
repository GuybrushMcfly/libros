import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock  # y otros que vayas creando

# --- Función logout definida antes del menú ---
def logout(authenticator):
    if st.session_state.get("cerrando_sesion"):
        st.session_state.clear()
        st.rerun()

    st.session_state["cerrando_sesion"] = True
    st.success("🔓 Cerrando sesión...")
    authenticator.logout("Cerrar sesión", "main")
    st.button("Continuar", on_click=st.rerun)

# --- Configuración inicial ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Login de usuario ---
login_info = login()

if not login_info:
    st.stop()

nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info

if not autenticado or "usuario" not in st.session_state:
    st.warning("🔒 Debés iniciar sesión para acceder.")
    st.stop()

if requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Menú de navegación principal ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon=":material/library_add:"),
    ],
    "📦 STOCK": [
        st.Page(ver_stock.ver_stock, title="Ver stock", icon=":material/inventory_2:"),
    ],
    "🔓 SESIÓN": [
        st.Page(lambda: logout(authenticator), title="Cerrar sesión", icon=":material/logout:")
    ]
}

pg = st.navigation(pages, position="top")
pg.run()
