import streamlit as st
import requests
import pandas as pd
import urllib.parse

# --- Función para buscar libros básicos ---
def buscar_libros_openlibrary(query, tipo="title"):
    query_escapado = urllib.parse.quote(query)
    url = f"https://openlibrary.org/search.json?{tipo}={query_escapado}&limit=15"
    res = requests.get(url)

    if res.status_code != 200:
        st.error(f"Error al consultar Open Library: código {res.status_code}")
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
            "Work Key": doc.get("key", "")  # necesario para consultar más detalles
        })

    return libros

# --- Función para obtener detalles de un libro ---
def obtener_detalles_libro(work_key):
    work_id = work_key.replace("/works/", "")
    url = f"https://openlibrary.org/works/{work_id}.json"
    res = requests.get(url)
    if res.status_code != 200:
        return {}

    data = res.json()
    detalles = {
        "Título": data.get("title", "Sin título"),
        "Descripción": data.get("description", {}).get("value") if isinstance(data.get("description"), dict)
                       else data.get("description", "Sin descripción"),
        "Temas": ", ".join(data.get("subjects", [])[:10]) if "subjects" in data else "No especificados"
    }
    return detalles

# --- Interfaz Streamlit ---
st.title("📚 Buscador de Libros con Detalles (Open Library API)")

# Busqueda por título
st.subheader("🔍 Buscar por Título")
titulo = st.text_input("Título (o parte):", key="titulo")
if st.button("Buscar título"):
    if titulo.strip():
        resultados = buscar_libros_openlibrary(titulo, tipo="title")
        if resultados:
            df = pd.DataFrame(resultados)
            df_simple = df.drop(columns=["Work Key"])
            st.dataframe(df_simple)

            seleccion = st.selectbox("Seleccioná un libro para ver más detalles:", df["Título"])
            fila = df[df["Título"] == seleccion].iloc[0]
            detalles = obtener_detalles_libro(fila["Work Key"])

            st.markdown(f"### 📖 {detalles.get('Título')}")
            st.markdown(f"**Autor/es:** {fila['Autor/es']}")
            st.markdown(f"**Año publicación:** {fila['Año publicación']}")
            st.markdown(f"**ISBN:** {fila['ISBN']}")
            st.markdown(f"**Temas:** {detalles.get('Temas')}")
            st.markdown(f"**Descripción:**\n\n{detalles.get('Descripción')}")
        else:
            st.warning("No se encontraron resultados.")

