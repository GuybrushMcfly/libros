import streamlit as st
import requests
import pandas as pd
import urllib.parse

# 👉 Función para buscar en Open Library por título o autor
def buscar_libros_openlibrary(query, tipo="title"):
    query_escapado = urllib.parse.quote(query)
    url = f"https://openlibrary.org/search.json?{tipo}={query_escapado}&limit=10"
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
            "Editorial": ", ".join(doc.get("publisher", ["No informada"]))[:60]  # Truncamos si es muy largo
        })

    return libros

# ---------- Interfaz Streamlit ----------
st.title("📚 Buscador de Libros (Open Library API)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 Buscar por Título")
    titulo = st.text_input("Título (o parte):")
    if st.button("Buscar título"):
        if titulo.strip():
            resultados = buscar_libros_openlibrary(titulo, tipo="title")
            if resultados:
                df = pd.DataFrame(resultados)
                st.dataframe(df)
            else:
                st.warning("No se encontraron resultados.")

with col2:
    st.subheader("🔍 Buscar por Autor")
    autor = st.text_input("Autor (o parte):")
    if st.button("Buscar autor"):
        if autor.strip():
            resultados = buscar_libros_openlibrary(autor, tipo="author")
            if resultados:
                df = pd.DataFrame(resultados)
                st.dataframe(df)
            else:
                st.warning("No se encontraron resultados.")
