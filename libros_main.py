import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock, buscar_libros

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

if autenticado is False:
    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()
elif autenticado is None:
    st.warning("🔐 Ingresá tus credenciales.")
    st.stop()
if requiere_cambio:
    st.warning("⚠️ Debés cambiar tu contraseña antes de continuar.")
    st.stop()

# --- Conteo rápido ---
def get_count(tabla):
    res = supabase.table(tabla).select("id", count="exact").limit(1).execute()
    return res.count or 0

autores_count = get_count("autores")
libros_count = get_count("libros")
editoriales_count = get_count("editoriales")

# --- Sidebar de navegación ---
st.sidebar.title("📚 Menú")
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"**Autores:** {autores_count}  \n"
    f"**Libros:** {libros_count}  \n"
    f"**Editoriales:** {editoriales_count}"
)
st.sidebar.markdown("---")

# --- Estructura del menú principal y submenú ---
menu = {
    "REGISTRO": [
        "Registrar libro",
        "Registrar editorial",
        "Registrar cliente"
    ],
    "STOCK": [
        "Ver stock",
        "Movimientos de stock"
    ],
    "BÚSQUEDA": [
        "Buscar libros"
    ],
    "VENTAS": [
        "Registrar venta",
        "Historial ventas"
    ],
    "PEDIDOS": [
        "Registrar pedido",
        "Ver pedidos"
    ],
    "REPORTES": []
}

secciones = [""] + list(menu.keys())
seccion = st.sidebar.selectbox("Sección", secciones)

subvista = None
if seccion and seccion in menu and len(menu[seccion]) > 0:
    subvista = st.sidebar.selectbox("Acción", menu[seccion])

st.sidebar.markdown("---")
authenticator.logout("Cerrar sesión", "sidebar")

st.sidebar.markdown("📚 *Gestión Librería v1.0*")

# --- Renderizar la vista según la selección ---
if seccion == "REGISTRO":
    if subvista == "Registrar libro":
        registrar_libro.registrar_libro()
    elif subvista == "Registrar editorial":
        st.info("🏷️ Módulo de registro de editoriales en proceso.")
    elif subvista == "Registrar cliente":
        st.info("👥 Módulo de registro de clientes en proceso.")

elif seccion == "STOCK":
    if subvista == "Ver stock":
        ver_stock.ver_stock()
    elif subvista == "Movimientos de stock":
        st.info("📦 Módulo de movimientos de stock en proceso.")

elif seccion == "BÚSQUEDA":
    if subvista == "Buscar libros":
        buscar_libros.buscar_libros()
    else:
        st.info("Seleccioná una acción en el menú lateral.")

elif seccion == "VENTAS":
    if subvista == "Registrar venta":
        st.info("💰 Módulo de registro de ventas en proceso.")
    elif subvista == "Historial ventas":
        st.info("📄 Módulo de historial de ventas en proceso.")

elif seccion == "PEDIDOS":
    if subvista == "Registrar pedido":
        st.info("📝 Módulo de registro de pedidos en proceso.")
    elif subvista == "Ver pedidos":
        st.info("📋 Módulo de visualización de pedidos en proceso.")

elif seccion == "REPORTES":
    st.info("📊 Módulo de reportes en proceso.")

else:
    st.info("Seleccioná una sección en el menú lateral para comenzar.")
