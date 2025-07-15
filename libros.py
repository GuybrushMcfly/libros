import streamlit as st
import pandas as pd
import requests
import urllib.parse
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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
            "Autor/es": ", ".join(doc.get("author_name", ["Desconocido"])),
            "Año publicación": doc.get("first_publish_year", "¿?"),
            "ISBN": ", ".join(doc.get("isbn", [])[:2]) if "isbn" in doc else "No informado",
            "Temas / Palabras clave": ", ".join(doc.get("subject", [])[:5]) if "subject" in doc else "No informados",
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
            df = df.sort_values(by="Título")  # Ordenar alfabéticamente
            df.fillna("No disponible", inplace=True)  # Evita errores por NaN

            # --- Configurar tabla tipo Excel ---
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(enabled=True)
            gb.configure_default_column(groupable=True, editable=False)
            gb.configure_selection("single", use_checkbox=False)
            grid_options = gb.build()

            # --- Mostrar tabla con AgGrid ---
            grid_response = AgGrid(
                df,
                gridOptions=grid_options,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                height=400,
                theme="alpine",
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False,
            )

            # --- Mostrar detalles si se seleccionó una fila ---
            selected = grid_response["selected_rows"]
            if selected:
                fila = selected[0]
                work_key = fila.get("Work Key", "")
                if work_key:
                    detalles = obtener_detalles_libro(work_key)

                    st.markdown("### 📖 Detalles del libro seleccionado")
                    st.markdown(f"**Título:** {fila['Título']}")
                    st.markdown(f"**Autor/es:** {fila['Autor/es']}")
                    st.markdown(f"**Año publicación:** {fila['Año publicación']}")
                    st.markdown(f"**ISBN:** {fila['ISBN']}")
                    st.markdown(f"**Temas:** {detalles.get('Temas')}")
                    st.markdown(f"**Descripción:**\n\n{detalles.get('Descripción')}")
        else:
            st.warning("No se encontraron resultados.")
