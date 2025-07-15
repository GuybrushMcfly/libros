import streamlit as st
import requests
import pandas as pd
import urllib.parse

# 👉 Función para buscar libros en Open Library
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
            "Temas / Palabras clave": ", ".join(doc.get("subject", [])[:5]) if "subject" in doc else "No informados"
        })

    return libros

# ---------- Interfaz Streamlit ----------
st.title("📚 Buscador de Libros (Open Library API)")

# 🔍 Búsqueda por título
st.subheader("🔍 Buscar por Título")
titulo = st.text_input("Título (o parte):", key="titulo")
if st.button("Buscar título"):
    if titulo.strip():
        resultados = buscar_libros_openlibrary(titulo, tipo="title")
        if resultados:
            df = pd.DataFrame(resultados)
            st.dataframe(df)
        else:
            st.warning("No se encontraron resultados.")

# 🔍 Búsqueda por autor
st.subheader("🔍 Buscar por Autor")
autor = st.text_input("Autor (o parte):", key="autor")
if st.button("Buscar autor"):
    if autor.strip():
        resultados = buscar_libros_openlibrary(autor, tipo="author")
        if resultados:
            df = pd.DataFrame(resultados)
            st.dataframe(df)
        else:
            st.warning("No se encontraron resultados.")
