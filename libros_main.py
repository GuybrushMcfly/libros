import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock  # Importá otras vistas cuando estén listas

# --- Configuración inicial ---
st.set_page_config(
    layout="wide",
    page_title="Gestión Librería",
    page_icon="📚",
    initial_sidebar_state="expanded"
)

# --- Login de usuario ---
login_info = login()
if not login_info or not isinstance(login_info, tuple) or len(login_info) != 6:
    st.stop()

nombre, autenticado, usuario, authenticator, supabase, requiere_cambio = login_info

# --- Validaciones de sesión ---
if not autenticado or "usuario" not in st.session_state:
    st.warning("🔒 Debés iniciar sesión para acceder.")
    st.stop()

if requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Función para cerrar sesión correctamente ---
def cerrar_sesion(authenticator):
    authenticator.logout("Cerrando sesión...", "main")
    st.session_state.clear()
    st.rerun()

# --- Sidebar de navegación ---
st.sidebar.title("📚 Menú de navegación")
st.sidebar.markdown(f"👤 **{nombre}**")
st.sidebar.markdown("---")

seccion = st.sidebar.selectbox("Sección", ["", "Libros", "Clientes", "Ventas"])

subvista = None
if seccion == "Libros":
    subvista = st.sidebar.selectbox("Acción", ["Registrar libro", "Ver stock"])
elif seccion == "Clientes":
    subvista = st.sidebar.selectbox("Acción", ["Nuevo pedido", "Ver pedidos"])
elif seccion == "Ventas":
    subvista = st.sidebar.selectbox("Acción", ["Nueva venta", "Historial de ventas"])

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Cerrar sesión", use_container_width=True, type="secondary"):
    cerrar_sesion(authenticator)

st.sidebar.markdown("📚 *Gestión Librería v1.0*")

# --- Renderizar la vista según la selección ---
if seccion == "Libros":
    if subvista == "Registrar libro":
        registrar_libro.registrar_libro()
    elif subvista == "Ver stock":
        ver_stock.ver_stock()
elif seccion == "Clientes":
    st.info("🧾 Módulo de pedidos aún no implementado.")
elif seccion == "Ventas":
    st.info("💰 Módulo de ventas aún no implementado.")
else:
    st.info("Seleccioná una sección en el menú lateral para comenzar.")
