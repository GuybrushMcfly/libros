import streamlit as st
from modules.supabase_conn import supabase
from modules.procesadores import procesar_autor

# --- Modal para agregar un nuevo autor ---
@st.dialog("Agregar nuevo autor")
def mostrar_modal_autor():
    nombres = st.text_input("Nombre/s")
    apellidos = st.text_input("Apellido/s")

    if st.button("Guardar autor"):
        datos = procesar_autor(nombres, apellidos)
        resultado = supabase.table("autores").insert(datos).execute()
        if resultado.data:
            st.success("✅ Autor agregado correctamente.")
            st.session_state["modal_autor"] = False
            st.rerun()
        else:
            st.error("❌ Error al agregar autor.")


# --- Modal para agregar nueva editorial ---
@st.dialog("Agregar nueva editorial")
def mostrar_modal_editorial():
    nombre = st.text_input("Nombre de la editorial").strip()

    if st.button("Guardar editorial"):
        if not nombre:
            st.warning("⚠️ El nombre no puede estar vacío.")
            return

        nombre_mayus = nombre.upper()

        existentes = supabase.table("editoriales")\
            .select("id")\
            .eq("nombre", nombre_mayus).execute().data

        if existentes:
            st.error("❌ Ya existe una editorial con ese nombre.")
            return

        resultado = supabase.table("editoriales").insert({
            "nombre": nombre_mayus
        }).execute()

        if resultado.data:
            st.success("✅ Editorial registrada correctamente.")
            st.session_state["modal_editorial"] = False
            st.session_state["editorial_ingresada"] = nombre_mayus
            st.rerun()
        else:
            st.error("❌ Error al guardar la editorial.")
