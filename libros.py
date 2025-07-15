import streamlit as st
import requests
import pandas as pd
import urllib.parse

# --- Buscar libros ---
def buscar_libros_openlibrary(query, tipo="title"):
    query_escapado = urllib.parse.quote(query)
    url = f"https://openlibrary.org/search.json?{tipo}={query_escapado}&limit=15"
    res = requests.get(url)
    if res.status_code != 200:
        st.error(f"Error al consultar Open Library: código {res.status_code}")
        return []

    data = res.json()
    libros = []
    for i, doc in enumerate(data.get("docs", [])):
        libros.append({
            "index": i,
            "Título": doc.get("title", "Sin título"),
            "Autor/es": ", ".join(doc.get("author_name", ["Desconocido"])),
            "Año publicación": doc.get("first_publish_year", "¿?"),
            "ISBN": ", ".join(doc.get("isbn", [])[:2]) if "isbn" in doc else "No informado",
            "Temas / Palabras clave": ", ".join(doc.get("subject", [])[:5]) if "subject" in doc else "No informados",
            "Work Key": doc.get("key", "")
        })

    return libros

# --- Detalles ---
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

# --- Streamlit UI ---
st.title("📚 Buscador de Libros (Open Library API)")

st.subheader("🔍 Buscar por Título")
titulo = st.text_input("Título (o parte):")

if st.button("Buscar título"):
    if titulo.strip():
        resultados = buscar_libros_openlibrary(titulo, tipo="title")
        if resultados:
            df = pd.DataFrame(resultados).sort_values("Título").reset_index(drop=True)
            df_simple = df[["Título", "Autor/es", "Año publicación"]]
            seleccion = st.radio("Seleccioná un libro haciendo clic en su título:", df_simple["Título"])

            fila = df[df["Título"] == seleccion].iloc[0]
            detalles = obtener_detalles_libro(fila["Work Key"])

            st.markdown("### 📖 Detalles del libro seleccionado")
            st.markdown(f"**Título:** {fila['Título']}")
            st.markdown(f"**Autor/es:** {fila['Autor/es']}")
            st.markdown(f"**Año publicación:** {fila['Año publicación']}")
            st.markdown(f"**ISBN:** {fila['ISBN']}")
            st.markdown(f"**Temas:** {detalles.get('Temas')}")
            st.markdown(f"**Descripción:**\n\n{detalles.get('Descripción')}")
        else:
            st.warning("No se encontraron resultados.")
