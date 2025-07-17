import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock  # y otros que vayas creando

# --- Configuración inicial ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Login de usuario ---
login_info = login()
if not login_info:
    st.stop()

nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info

# --- Controles post-login ---
if autenticado is False:
    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

elif autenticado is None:
    st.info("🔐 Por favor ingresá tus credenciales.")
    st.stop()

elif requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Función para cerrar sesión desde el menú ---
def cerrar_sesion():
    authenticator.logout("Cerrar sesión", "main")
    st.success("🔓 Sesión cerrada. Redirigiendo...")
    st.rerun()

# --- Menú de navegación principal ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon=":material/library_add:"),
    ],
    "📦 STOCK": [
        st.Page(ver_stock.ver_stock, title="Ver stock", icon=":material/inventory_2:"),
    ],
    "🔓 SESIÓN": [
        st.Page(cerrar_sesion, title="Cerrar sesión", icon=":material/logout:")
    ]
}

pg = st.navigation(pages, position="top")
pg.run()
