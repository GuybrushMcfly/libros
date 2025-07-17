import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import time

from modules.supabase_conn import supabase
from modules.dialogos import mostrar_modal_autor, mostrar_modal_editorial
from modules.procesadores import limpiar_valores_nulos

def registrar_libro():
    st.title("📘 Registrar nuevo libro")

    # --- Cargar datos desde Supabase ---
    df_autores = pd.DataFrame(
        supabase.table("autores").select("id, nombre_formal").order("nombre_formal").execute().data
    )
    df_categorias = pd.DataFrame(
        supabase.table("categorias").select("id, nombre").order("nombre").execute().data
    )
    df_subcategorias = pd.DataFrame(
        supabase.table("subcategorias").select("id, nombre, categoria_id").order("nombre").execute().data
    )
    df_editoriales = pd.DataFrame(
        supabase.table("editoriales").select("id, nombre").order("nombre").execute().data
    ) if supabase.table("editoriales").select("id").execute().data else pd.DataFrame(columns=["id", "nombre"])

    # --- Categoría/Subcategoría en cascada ---
    col_cat, col_subcat = st.columns(2)
    with col_cat:
        categoria_nombre = st.selectbox("Categoría", ["-Seleccioná-"] + df_categorias["nombre"].tolist())
        categoria_id = df_categorias[df_categorias["nombre"] == categoria_nombre]["id"].values[0] if categoria_nombre != "-Seleccioná-" else None
    with col_subcat:
        opciones_sub = ["-Seleccioná-"]
        subcategoria_id = None
        if categoria_id:
            subcats = df_subcategorias[df_subcategorias["categoria_id"] == categoria_id]
            opciones_sub += subcats["nombre"].tolist()
        subcat_nombre = st.selectbox("Subcategoría", opciones_sub)
        if categoria_id and subcat_nombre != "-Seleccioná-":
            subcategoria_id = subcats[subcats["nombre"] == subcat_nombre]["id"].values[0]

    # --- Autor principal y coautores ---
    col_autor, col_editorial = st.columns(2)
    with col_autor:
        seleccion_autor = st.selectbox("Autor", ["- Seleccionar autor -"] + df_autores["nombre_formal"].tolist(), key="autor_selector")
        if st.button("➕ Agregar autor"):
            st.session_state["modal_autor"] = True

    with col_editorial:
        seleccion_editorial = st.selectbox("Editorial", ["- Seleccionar editorial -"] + df_editoriales["nombre"].tolist(), key="editorial_selector")
        if st.button("➕ Agregar editorial"):
            st.session_state["modal_editorial"] = True

    if st.session_state.get("modal_autor"):
        mostrar_modal_autor()
    if st.session_state.get("modal_editorial"):
        mostrar_modal_editorial()

    autor_id = df_autores[df_autores["nombre_formal"] == seleccion_autor]["id"].values[0] if seleccion_autor != "- Seleccionar autor -" else None
    editorial_id = df_editoriales[df_editoriales["nombre"] == seleccion_editorial]["id"].values[0] if seleccion_editorial != "- Seleccionar editorial -" else None

    # --- Coautores ---
    if "coautores" not in st.session_state:
        st.session_state["coautores"] = []

    st.markdown("#### Coautores")
    for i, seleccion in enumerate(st.session_state["coautores"]):
        coautor = st.selectbox(f"Coautor #{i+1}", ["- Seleccionar -"] + df_autores["nombre_formal"].tolist(), key=f"coautor_{i}")
        st.session_state["coautores"][i] = coautor

    if len(st.session_state["coautores"]) < 2:
        if st.button("➕ Registrar coautor"):
            st.session_state["coautores"].append("- Seleccionar -")
            st.rerun()

    # --- Validación mínima para avanzar ---
    if all([categoria_id, subcategoria_id, autor_id, editorial_id]):
        with st.form("formulario_libro"):
            titulo = st.text_input("Título del libro")

            # --- CAMPOS COMENTADOS (no se usan actualmente) ---
            # col1, col2, col3 = st.columns(3)
            # isbn = col1.text_input("ISBN")
            # anio = col2.number_input("Año de publicación", min_value=1000, max_value=2100, step=1)
            # idioma = col3.selectbox("Idioma", ["-Seleccioná-", "ESPAÑOL", "INGLÉS", "FRANCÉS", "ITALIANO", "OTRO"])

            col4, col5, col6 = st.columns(3)
            formato = col4.selectbox("Formato", ["-Seleccioná-", "TAPA DURA", "TAPA BLANDA", "BOLSILLO", "REVISTA"])
            estado = col5.selectbox("Estado", ["-Seleccioná-", "NUEVO", "USADO", "REPLICA", "ANTIGUO"])
            ubicacion = col6.text_input("Ubicación")

            # palabras_clave = st.text_input("Palabras clave (coma)")

            col_a, col_b, col_c, col_d = st.columns(4)
            precio_costo = col_a.number_input("💰 Precio de compra", min_value=0.0, step=0.01)
            precio_venta = col_b.number_input("🏷️ Precio de venta", min_value=0.0, step=0.01)
            cantidad = col_c.number_input("📦 Cantidad en stock", min_value=1, step=1)
            tipo_ingreso = col_d.selectbox("Tipo ingreso", ["-Seleccioná-", "STOCK HEREDADO", "INGRESO NUEVO"])

            # --- CAMPO ACTIVO: Observaciones como último ---
            observaciones = st.text_area("Observaciones")

            if st.form_submit_button("Registrar libro"):
                if not titulo.strip():
                    st.error("⚠️ Título obligatorio.")
                    st.stop()
                if tipo_ingreso == "-Seleccioná-":
                    st.warning("⚠️ Elegí tipo de ingreso.")
                    st.stop()

                datos_libro = limpiar_valores_nulos({
                    "titulo": titulo.strip().upper(),
                    # "autor_id": autor_id,
                    "editorial_id": editorial_id,
                    # "anio": int(anio) if anio else None,
                    # "idioma": idioma if idioma != "-Seleccioná-" else None,
                    "formato": formato if formato != "-Seleccioná-" else None,
                    "estado": estado if estado != "-Seleccioná-" else None,
                    # "descripcion": descripcion.strip(),
                    # "isbn": isbn.strip(),
                    "ubicacion": ubicacion.strip(),
                    # "palabras_clave": [p.strip() for p in palabras_clave.split(",")] if palabras_clave else None,
                    "observaciones": observaciones.strip() if observaciones else None,
                    "fecha_creacion": datetime.now().isoformat(),
                    "subcategoria_id": subcategoria_id
                })

                try:
                    libro = supabase.table("libros").insert(datos_libro).execute().data
                    if not libro:
                        st.error("❌ Error al insertar libro.")
                        return
                    libro_id = libro[0]["id"]

                    # Insertar relación libro-autor principal
                    supabase.table("libros_autores").insert({
                        "libro_id": libro_id,
                        "autor_id": autor_id,
                        "orden": 1
                    }).execute()

                    # Insertar coautores si hay
                    for idx, nombre in enumerate(st.session_state["coautores"]):
                        if nombre != "- Seleccionar -":
                            fila = df_autores[df_autores["nombre_formal"] == nombre]
                            if not fila.empty:
                                supabase.table("libros_autores").insert({
                                    "libro_id": libro_id,
                                    "autor_id": fila.iloc[0]["id"],
                                    "orden": idx + 2
                                }).execute()

                    supabase.table("stock").insert({
                        "libro_id": libro_id,
                        "cantidad_actual": int(cantidad),
                        "precio_costo": float(precio_costo),
                        "precio_venta_actual": float(precio_venta),
                        "fecha_ultima_actualizacion": datetime.now().isoformat()
                    }).execute()

                    supabase.table("movimientos_stock").insert({
                        "libro_id": libro_id,
                        "tipo": tipo_ingreso,
                        "cantidad": int(cantidad),
                        "precio_unitario": float(precio_costo),
                        "fecha": datetime.now().isoformat(),
                        "detalle": "Alta inicial desde formulario"
                    }).execute()

                    st.success("✅ Libro y autor/es registrado/s.")
                    time.sleep(2)
                    
                    # --- LIMPIEZA de formulario tras inserción exitosa ---
                    for key in list(st.session_state.keys()):
                        if key.startswith("libro_") or key in [
                            "titulo", "editorial", "anio", "idioma", "formato", "estado",
                            "descripcion", "isbn", "ubicacion", "palabras_clave",
                            "precio_costo", "precio_venta", "cantidad", "tipo_ingreso",
                            "autor_selector", "cat", "subcat", "editorial_selector"
                        ] or key.startswith("coautor_"):
                            del st.session_state[key]
                    
                    st.session_state["autor_selector"] = "- Seleccionar autor -"
                    st.session_state["cat"] = "-Seleccioná-"
                    st.session_state["subcat"] = "-Seleccioná-"
                    st.session_state["editorial_selector"] = "- Seleccionar editorial -"
                    st.session_state["coautores"] = []
                    st.rerun()


                
                except Exception as e:
                    st.error("❌ Error al registrar.")
                    st.exception(e)
