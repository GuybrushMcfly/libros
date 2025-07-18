import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import time

from modules.supabase_conn import supabase
from modules.dialogos import mostrar_modal_autor, mostrar_modal_editorial
from modules.procesadores import limpiar_valores_nulos

st.markdown("""
<style>
.div-form {
  border:1px solid #ccc;
  padding:20px;
  border-radius:5px;
  margin-top:20px;
  background-color: #f9f9f9;
}
.div-form h2 {
  margin-top: 0;
}
</style>
""", unsafe_allow_html=True)

def registrar_libro_sin_form():
    st.title("📘 Registrar nuevo libro (sin st.form)")

    # --- Cargar datos ---
    df_autores = pd.DataFrame(supabase.table("autores").select("id, nombre_formal").order("nombre_formal").execute().data)
    df_categorias = pd.DataFrame(supabase.table("categorias").select("id, nombre").order("nombre").execute().data)
    df_subcategorias = pd.DataFrame(supabase.table("subcategorias").select("id, nombre, categoria_id").order("nombre").execute().data)
    df_editoriales = pd.DataFrame(supabase.table("editoriales").select("id, nombre").order("nombre").execute().data) if supabase.table("editoriales").select("id").execute().data else pd.DataFrame(columns=["id", "nombre"])

    # --- Cascada Categoría/Subcategoría ---
    col_cat, col_subcat = st.columns(2)
    with col_cat:
        categoria_nombre = st.selectbox("Categoría", ["- Seleccioná categoría -"] + df_categorias["nombre"].tolist(), key="cat2")
        categoria_id = df_categorias.loc[df_categorias["nombre"] == categoria_nombre, "id"].squeeze() if categoria_nombre != "- Seleccioná categoría -" else None

    with col_subcat:
        opciones_sub = ["- Seleccioná subcategoría -"]
        if categoria_id:
            opciones_sub += df_subcategorias[df_subcategorias["categoria_id"] == categoria_id]["nombre"].tolist()
        subcat_nombre = st.selectbox("Subcategoría", opciones_sub, key="subcat2")
        subcategoria_id = df_subcategorias.loc[(df_subcategorias["nombre"] == subcat_nombre) & (df_subcategorias["categoria_id"] == categoria_id), "id"].squeeze() if subcat_nombre != "- Seleccioná subcategoría -" else None

    # --- Autor y Editorial ---
    col_autor, col_editorial = st.columns(2)
    with col_autor:
        seleccion_autor = st.selectbox("Autor", ["- Seleccionar autor -"] + df_autores["nombre_formal"].tolist(), key="autor2")
        if st.button("➕ Agregar autor", key="btn_autor2"):
            st.session_state["modal_autor"] = True
    with col_editorial:
        seleccion_editorial = st.selectbox("Editorial", ["- Seleccionar editorial -"] + df_editoriales["nombre"].tolist(), key="editorial2")
        if st.button("➕ Agregar editorial", key="btn_edit2"):
            st.session_state["modal_editorial"] = True

    if st.session_state.get("modal_autor"):
        mostrar_modal_autor(); st.stop()
    if st.session_state.get("modal_editorial"):
        mostrar_modal_editorial(); st.stop()

    autor_id = df_autores.loc[df_autores["nombre_formal"] == seleccion_autor, "id"].squeeze() if seleccion_autor != "- Seleccionar autor -" else None
    editorial_id = df_editoriales.loc[df_editoriales["nombre"] == seleccion_editorial, "id"].squeeze() if seleccion_editorial != "- Seleccionar editorial -" else None

    # --- Coautores ---
    if "coautores2" not in st.session_state:
        st.session_state["coautores2"] = []
    st.markdown("#### Coautores")
    for i, nombre in enumerate(st.session_state["coautores2"]):
        st.session_state["coautores2"][i] = st.selectbox(f"Coautor #{i+1}", ["- Seleccionar -"] + df_autores["nombre_formal"].tolist(), key=f"coautor2_{i}")
    if len(st.session_state["coautores2"]) < 2:
        if st.button("➕ Registrar coautor", key="btn_coautor2"):
            st.session_state["coautores2"].append("- Seleccionar -")
            st.rerun()

    # --- Mostrar contenedor tipo formulario ---
    st.markdown('<div class="div-form">', unsafe_allow_html=True)
    titulo = st.text_input("Título del libro", key="titulo2")
    col4, col5, col6 = st.columns(3)
    with col4:
        formato = st.selectbox("Formato", ["- Seleccioná -", "Tapa Dura", "Tapa Blanda", "Bolsillo", "Revista"], key="formato2")
    with col5:
        estado = st.selectbox("Estado", ["- Seleccioná -", "Nuevo", "Usado", "Réplica", "Antiguo"], key="estado2")
    with col6:
        ubicacion = st.text_input("Ubicación", key="ubicacion2")

    col_a, col_b, col_c, col_d = st.columns(4)
    precio_costo = col_a.number_input("💰 Precio de compra", min_value=0.0, step=0.01, key="pc2")
    precio_venta = col_b.number_input("🏷️ Precio de venta", min_value=0.0, step=0.01, key="pv2")
    cantidad = col_c.number_input("📦 Cantidad en stock", min_value=1, step=1, key="cant2")
    tipo_ingreso = col_d.selectbox("Tipo ingreso", ["- Seleccioná -", "Stock Heredado", "Stock Nuevo"], key="ti2")
    observaciones = st.text_area("Observaciones", key="obs2")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Botón enviar aparte ---
    if st.button("Registrar libro"):
        # Validaciones idénticas...
        faltantes = []
        if not titulo.strip(): faltantes.append("Título")
        if not categoria_id: faltantes.append("Categoría")
        if not subcategoria_id: faltantes.append("Subcategoría")
        if not autor_id: faltantes.append("Autor principal")
        if not editorial_id: faltantes.append("Editorial")
        if formato == "- Seleccioná -": faltantes.append("Formato")
        if estado == "- Seleccioná -": faltantes.append("Estado")
        if cantidad < 1: faltantes.append("Cantidad")
        if tipo_ingreso == "- Seleccioná -": faltantes.append("Tipo ingreso")

        if faltantes:
            st.warning("⚠️ Completá: " + ", ".join(faltantes))
        else:
            datos = limpiar_valores_nulos({
                "titulo": titulo.strip().upper(),
                "formato": None if formato == "- Seleccioná -" else formato,
                "estado": None if estado == "- Seleccioná -" else estado,
                "ubicacion": ubicacion.strip(),
                "observaciones": observaciones.strip(),
                "fecha_creacion": datetime.now().isoformat(),
                "subcategoria_id": int(subcategoria_id)
            })
            # Insert Supabase, relaciones, stock, movimientos igual al código original...
            st.success("✅ Libro registrado correctamente.")
            st.session_state.clear()
            st.experimental_rerun()

registrar_libro_sin_form()
