import streamlit as st
import requests
import pandas as pd


API_KEY = st.secrets["GOOGLE_BOOKS_API_KEY"]

# 👉 Función para buscar en Google Books API
def buscar_libros_google(query, tipo="intitle"):
    url = f"https://www.googleapis.com/books/v1/volumes?q={tipo}:{query}&maxResults=10&key={API_KEY}"
    res = requests.get(url)

    if res.status_code != 200:
        st.error("Error al consultar la API")
        return []

    data = res.json()
    libros = []

    for item in data.get("items", []):
        info = item.get("volumeInfo", {})
        libros.append({
            "Título": info.get("title", "Sin título"),
            "Autor/es": ", ".join(info.get("authors", ["Desconocido"])),
            "Editorial": info.get("publisher", "No informada")
        })

    return libros

# ---------- Interfaz Streamlit ----------
st.title("📚 Buscador de Libros (Google Books API)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 Buscar por Título")
    titulo = st.text_input("Título (o parte):")
    if st.button("Buscar título"):
        if titulo.strip():
            resultados = buscar_libros_google(titulo, tipo="intitle")
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
            resultados = buscar_libros_google(autor, tipo="inauthor")
            if resultados:
                df = pd.DataFrame(resultados)
                st.dataframe(df)
            else:
                st.warning("No se encontraron resultados.")
