import streamlit as st
import pandas as pd
import requests
import urllib.parse
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

def buscar_libros_openlibrary(query, tipo="title"):
    query_escapado = urllib.parse.quote(query)
    url = f"https://openlibrary.org/search.json?{tipo}={query_escapado}&limit=15"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Error al consultar Open Library")
        return []
    data = res.json()
    libros = []
    for doc in data.get("docs", []):
        libros.append({
            "Título": doc.get("title", "Sin título"),
            "Autor": ", ".join(doc.get("author_name", ["Desconocido"])),
            "Año": doc.get("first_publish_year", "¿?"),
            "ISBN": ", ".join(doc.get("isbn", [])[:2]) if "isbn" in doc else "No informado",
            "Temas": ", ".join(doc.get("subject", [])[:3]) if "subject" in doc else "No informados",
            "Work Key": doc.get("key", "")
        })
    return libros

def obtener_detalles_libro(work_key):
    work_id = work_key.replace("/works/", "")
    url = f"https://openlibrary.org/works/{work_id}.json"
    res = requests.get(url)
    if res.status_code != 200:
        return {}
    data = res.json()
    descripcion = ""
    if isinstance(data.get("description"), dict):
        descripcion = data.get("description", {}).get("value", "")
    else:
        descripcion = data.get("description", "Sin descripción")
    return {
        "Descripción": descripcion,
        "Temas": ", ".join(data.get("subjects", [])[:10]) if "subjects" in data else "No especificados"
    }

# --- Interfaz Streamlit ---
st.title("📚 Buscador de Libros con selección directa")
st.subheader("🔍 Buscar por Título")
titulo = st.text_input("Título (o parte):")

if st.button("Buscar título"):
    if titulo.strip():
        resultados = buscar_libros_openlibrary(titulo, tipo="title")
        if resultados:
            df = pd.DataFrame(resultados)
            df = df.sort_values(by="Título")
            df.fillna("No disponible", inplace=True)
            
            # --- Configurar tabla tipo Excel ---
            gb = GridOptionsBuilder.from_dataframe(df)
            
            # Configuración general
            gb.configure_pagination(enabled=True, paginationPageSize=10)
            gb.configure_side_bar()
            gb.configure_default_column(
                groupable=True, 
                value=True, 
                enableRowGroup=True, 
                aggFunc="sum", 
                editable=False,
                resizable=True,
                sortable=True,
                filterable=True
            )
            
            # Configurar selección
            gb.configure_selection(
                selection_mode="single", 
                use_checkbox=False,
                pre_selected_rows=[]
            )
            
            # Configurar columnas específicas
            gb.configure_column("Título", width=200, headerCheckboxSelection=False)
            gb.configure_column("Autor", width=150)
            gb.configure_column("Año", width=80, type=["numericColumn"])
            gb.configure_column("ISBN", width=120)
            gb.configure_column("Temas", width=200)
            gb.configure_column("Work Key", hide=True)  # Ocultar esta columna
            
            # Configurar grid options
            gb.configure_grid_options(
                domLayout='normal',
                enableRangeSelection=True,
                enableBrowserTooltips=True,
                rowSelection='single'
            )
            
            grid_options = gb.build()
            
            # --- Mostrar tabla con AgGrid ---
            st.markdown("### 📋 Resultados de la búsqueda")
            st.markdown("*Haz clic en una fila para ver los detalles del libro*")
            
            grid_response = AgGrid(
                df,
                gridOptions=grid_options,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                height=400,
                width='100%',
                theme="streamlit",  # Cambiado a tema streamlit
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False,
                reload_data=False
            )
            
            # --- Mostrar detalles si se seleccionó una fila ---
            selected = grid_response["selected_rows"]
            if selected:
                fila = selected[0]
                work_key = fila.get("Work Key", "")
                if work_key:
                    detalles = obtener_detalles_libro(work_key)
                    
                    # Mostrar detalles en una caja expandida
                    with st.expander("📖 Detalles del libro seleccionado", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**📚 Título:** {fila['Título']}")
                            st.markdown(f"**✍️ Autor:** {fila['Autor']}")
                            st.markdown(f"**📅 Año:** {fila['Año']}")
                            st.markdown(f"**📖 ISBN:** {fila['ISBN']}")
                        
                        with col2:
                            st.markdown(f"**🏷️ Temas:** {detalles.get('Temas', 'No especificados')}")
                        
                        st.markdown("**📝 Descripción:**")
                        descripcion = detalles.get('Descripción', 'Sin descripción disponible')
                        if len(descripcion) > 500:
                            st.markdown(descripcion[:500] + "...")
                        else:
                            st.markdown(descripcion)
                else:
                    st.warning("No se pudo obtener información adicional de este libro.")
        else:
            st.warning("No se encontraron resultados.")
    else:
        st.warning("Por favor ingresa un título para buscar.")

# Agregar información adicional en la barra lateral
st.sidebar.markdown("### ℹ️ Información")
st.sidebar.markdown("""
- **Selecciona una fila** haciendo clic en ella
- **Filtra** usando los iconos de filtro en las columnas
- **Ordena** haciendo clic en los encabezados
- **Pagina** usando los controles en la parte inferior
""")

st.sidebar.markdown("### 🔍 Características")
st.sidebar.markdown("""
- ✅ Tabla tipo Excel interactiva
- ✅ Selección de filas
- ✅ Filtros por columna
- ✅ Ordenamiento
- ✅ Paginación
- ✅ Detalles expandidos
""")
