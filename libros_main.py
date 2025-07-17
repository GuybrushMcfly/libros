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

# --- Sidebar con navegación ---
with st.sidebar:
    # Header del sidebar con usuario
    st.markdown(f"### 👤 {nombre}")
    st.markdown("---")
    
    # Menú de navegación con selectbox
    st.markdown("### 📋 Navegación")
    
    page_options = {
        "📥 Registrar libro": "registrar_libro",
        "📦 Ver stock": "ver_stock"
    }
    
    # Selectbox para navegación
    selected_page = st.selectbox(
        "Seleccionar página:",
        options=list(page_options.keys()),
        index=0
    )
    
    # Obtener la página seleccionada
    current_page = page_options[selected_page]
    
    st.markdown("---")
    
    # Métricas o información útil
    st.markdown("### 📊 Resumen")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📚 Libros", "---")
    with col2:
        st.metric("💰 Stock", "---")
    
    st.markdown("---")
    
    # Botón de logout
    st.markdown("### 🔓 Sesión")
    if st.button("🚪 Cerrar sesión", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.success("🔓 Sesión cerrada exitosamente")
        st.rerun()
    
    # Información adicional en el pie del sidebar
    st.markdown("---")
    st.markdown("*Gestión Librería v1.0*")

# --- Contenido principal ---
st.title("📚 Gestión Librería")

# Mostrar breadcrumb
st.markdown(f"📍 **{selected_page}**")
st.markdown("---")

# Ejecutar la función correspondiente según la página seleccionada
if current_page == 'registrar_libro':
    registrar_libro.registrar_libro()
elif current_page == 'ver_stock':
    ver_stock.ver_stock()
