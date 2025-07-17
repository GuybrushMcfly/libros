import streamlit as st
from modules.auth import login
from views import registrar_libro, ver_stock

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

# --- Función para cerrar sesión ---
def cerrar_sesion():
    st.session_state.clear()
    st.success("🔓 Sesión cerrada exitosamente")
    st.rerun()

# --- Función placeholder para páginas futuras ---
def pagina_placeholder():
    st.info("🚧 Esta función estará disponible próximamente")
    st.markdown("---")
    st.markdown("**Características planeadas:**")
    st.markdown("- Funcionalidad completa")
    st.markdown("- Interfaz intuitiva")
    st.markdown("- Integración con base de datos")

# --- Sidebar con información del usuario ---
with st.sidebar:
    # Header del sidebar con usuario
    st.markdown(f"### 👤 {nombre}")
    st.markdown("---")
    
    # Información adicional
    st.markdown("**🕒 Último acceso:**")
    st.markdown("*Hoy, 10:30 AM*")
    
    st.markdown("---")
    
    # Botón de logout en sidebar
    if st.button("🚪 Cerrar sesión", use_container_width=True, type="secondary"):
        cerrar_sesion()
    
    st.markdown("---")
    st.markdown("*Gestión Librería v1.0*")

# --- Menú de navegación principal en sidebar ---
pages = {
    "📥 GESTIÓN DE INGRESOS": [
        st.Page(registrar_libro.registrar_libro, title="Registrar libro", icon=":material/library_add:"),
        st.Page(pagina_placeholder, title="Importar catálogo", icon=":material/upload:"),
        st.Page(pagina_placeholder, title="Editar libros", icon=":material/edit:"),
    ],
    "📦 CONTROL DE STOCK": [
        st.Page(ver_stock.ver_stock, title="Ver stock", icon=":material/inventory_2:"),
        st.Page(pagina_placeholder, title="Stock bajo", icon=":material/warning:"),
        st.Page(pagina_placeholder, title="Movimientos", icon=":material/sync_alt:"),
    ],
    "📊 REPORTES": [
        st.Page(pagina_placeholder, title="Ventas", icon=":material/trending_up:"),
        st.Page(pagina_placeholder, title="Inventario", icon=":material/storage:"),
        st.Page(pagina_placeholder, title="Ganancias", icon=":material/monetization_on:"),
    ],
    "⚙️ CONFIGURACIÓN": [
        st.Page(pagina_placeholder, title="Usuarios", icon=":material/people:"),
        st.Page(pagina_placeholder, title="Categorías", icon=":material/category:"),
        st.Page(pagina_placeholder, title="Backup", icon=":material/backup:"),
    ]
}

# --- Ejecutar navegación en sidebar ---
pg = st.navigation(pages, position="sidebar")
pg.run()
