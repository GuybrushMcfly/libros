import streamlit as st

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Mi Aplicación",
        page_icon="🏠",
        layout="wide"
    )
    
    # CSS personalizado para el menú
    st.markdown("""
    <style>
    .nav-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-bottom: 2px solid #e6e9ef;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Título principal
    st.title("🏠 Mi Aplicación Web")
    
    # Contenedor del menú de navegación
    with st.container():
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        
        # Menú principal horizontal
        col1, col2, col3 = st.columns([2, 2, 6])
        
        with col1:
            opcion_principal = st.selectbox(
                "📋 Menú Principal",
                ["Análisis", "Configuración"],
                key="menu_principal"
            )
        
        with col2:
            if opcion_principal == "Análisis":
                subopcion = st.selectbox(
                    "📊 Análisis",
                    ["Datos", "Reportes"],
                    key="submenu_analisis"
                )
            else:  # Configuración
                subopcion = st.selectbox(
                    "⚙️ Configuración",
                    ["Usuario", "Sistema"],
                    key="submenu_configuracion"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Separador visual
    st.markdown("---")
    
    # Mostrar selección actual
    st.info(f"Navegación actual: **{opcion_principal}** → **{subopcion}**")
    
    # Contenido basado en la selección
    if opcion_principal == "Análisis":
        if subopcion == "Datos":
            st.header("📊 Sección de Datos")
            st.write("Contenido para análisis de datos...")
        elif subopcion == "Reportes":
            st.header("📈 Sección de Reportes")
            st.write("Contenido para reportes...")
    
    elif opcion_principal == "Configuración":
        if subopcion == "Usuario":
            st.header("👤 Configuración de Usuario")
            st.write("Contenido para configuración de usuario...")
        elif subopcion == "Sistema":
            st.header("🔧 Configuración del Sistema")
            st.write("Contenido para configuración del sistema...")

if __name__ == "__main__":
    main()
