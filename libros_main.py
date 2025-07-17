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

# --- Mostrar nombre y botón de logout arriba ---
col1, col2 = st.columns([8, 1])
with col1:
    st.markdown(f"👤 {nombre}")
with col2:
    authenticator.logout("🚪", "main")  # Botón de logout arriba a la derecha

# --- Menú de navegación principal ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon=":material/library_add:"),
    ],
    "📦 STOCK": [
        st.Page(ver_stock.ver_stock, title="Ver stock", icon=":material/inventory_2:"),
    ]
}

pg = st.navigation(pages, position="top")
pg.run()
