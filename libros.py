import streamlit as st
import requests
import pandas as pd
import urllib.parse

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
st.title("📚 Buscador de Libros con Detalles (Open Library API)")

st.subheader("🔍 Buscar por Título")
titulo = st.text_input("Título (o parte):")
if st.button("Buscar título"):
    if titulo.strip():
        resultados = buscar_libros_openlibrary(titulo, tipo="title")
        if resultados:
            df = pd.DataFrame(resultados)
            df = df.sort_values("Título")
            df_simple = df[["Título", "Autor/es", "Año publicación"]].reset_index(drop=True)
            st.dataframe(df_simple)

            seleccion = st.radio("📌 Seleccioná un título para ver detalles:", df_simple["Título"])
            fila = df[df["Título"] == seleccion].iloc[0]
            detalles = obtener_detalles_libro(fila["Work Key"])

            st.markdown("### 📖 Detalles del libro")
            st.markdown(f"**Título:** {fila['Título']}")
            st.markdown(f"**Autor/es:** {fila['Autor/es']}")
            st.markdown(f"**Año publicación:** {fila['Año publicación']}")
            st.markdown(f"**ISBN:** {fila['ISBN']}")
            st.markdown(f"**Temas:** {detalles.get('Temas')}")
            st.markdown(f"**Descripción:**\n\n{detalles.get('Descripción')}")
        else:
            st.warning("No se encontraron resultados.")
