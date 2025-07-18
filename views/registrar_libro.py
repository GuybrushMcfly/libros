import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import time

from modules.supabase_conn import supabase
from modules.modal import mostrar_modal_autor, mostrar_modal_editorial
from modules.procesadores import limpiar_valores_nulos

# --- CACHÉ de autores y editoriales ---
@st.cache_data
def cargar_autores():
    return pd.DataFrame(supabase.table("autores").select("id, nombre_formal").order("nombre_formal").execute().data)

@st.cache_data
def cargar_editoriales():
    data = supabase.table("editoriales").select("id, nombre").order("nombre").execute().data
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "nombre"])

def registrar_libro():
    st.title("📘 Registrar nuevo libro")

    # --- Cargar datos desde Supabase ---
    df_autores = cargar_autores()
    df_categorias = pd.DataFrame(
        supabase.table("categorias").select("id, nombre").order("nombre").execute().data
    )
    df_subcategorias = pd.DataFrame(
        supabase.table("subcategorias").select("id, nombre, categoria_id").order("nombre").execute().data
    )
    df_editoriales = cargar_editoriales()

    # --- Categoría/Subcategoría en cascada ---
    col_cat, col_subcat = st.columns(2)
    with col_cat:
        categoria_nombre = st.selectbox("Categoría", ["- Seleccioná categoría -"] + df_categorias["nombre"].tolist(), key="cat")
        categoria_id = None
        if categoria_nombre != "- Seleccioná categoría -":
            fila = df_categorias[df_categorias["nombre"] == categoria_nombre]
            if not fila.empty:
                categoria_id = fila.iloc[0]["id"]
    
    with col_subcat:
        opciones_sub = ["- Seleccioná subcategoría -"]
        subcategoria_id = None
        if categoria_id:
            subcats = df_subcategorias[df_subcategorias["categoria_id"] == categoria_id]
            opciones_sub += subcats["nombre"].tolist()
        subcat_nombre = st.selectbox("Subcategoría", opciones_sub, key="subcat")
        if categoria_id and subcat_nombre != "- Seleccioná subcategoría -":
            fila_sub = subcats[subcats["nombre"] == subcat_nombre]
            if not fila_sub.empty:
                subcategoria_id = fila_sub.iloc[0]["id"]

    # --- Autor principal y coautores ---
    col_autor, col_editorial = st.columns(2)
    with col_autor:
        seleccion_autor = st.selectbox("Autor", ["- Seleccionar autor -"] + df_autores["nombre_formal"].tolist(), key="autor_selector")
        if st.button("➕ Agregar autor, type = "primary""):
            st.session_state["modal_autor"] = True

    with col_editorial:
        seleccion_editorial = st.selectbox("Editorial", ["- Seleccionar editorial -"] + df_editoriales["nombre"].tolist(), key="editorial_selector")
        if st.button("➕ Agregar editorial", type = "primary"):
            st.session_state["modal_editorial"] = True

    # --- Modales con limpieza de caché al agregar (importante) ---
    if st.session_state.get("modal_autor"):
        mostrar_modal_autor()
        cargar_autores.clear()  # Limpia el caché de autores tras agregar uno nuevo
        st.stop()
    
    if st.session_state.get("modal_editorial"):
        mostrar_modal_editorial()
        cargar_editoriales.clear()  # Limpia el caché de editoriales tras agregar uno nuevo
        st.stop()
   
    # --- Asignación segura de autor_id ---
    autor_id = None
    if seleccion_autor != "- Seleccionar autor -":
        fila_autor = df_autores[df_autores["nombre_formal"] == seleccion_autor]
        if not fila_autor.empty:
            autor_id = fila_autor.iloc[0]["id"]

    # --- Asignación segura de editorial_id ---
    editorial_id = None
    if seleccion_editorial != "- Seleccionar editorial -":
        fila_editorial = df_editoriales[df_editoriales["nombre"] == seleccion_editorial]
        if not fila_editorial.empty:
            editorial_id = fila_editorial.iloc[0]["id"]

    # --- Coautores ---
    if "coautores" not in st.session_state:
        st.session_state["coautores"] = []

    st.markdown("#### Coautores")
    for i, seleccion in enumerate(st.session_state["coautores"]):
        coautor = st.selectbox(f"Coautor #{i+1}", ["- Seleccionar -"] + df_autores["nombre_formal"].tolist(), key=f"coautor_{i}")
        st.session_state["coautores"][i] = coautor

    if len(st.session_state["coautores"]) < 2:
        if st.button("➕ Registrar coautor", type = "primary"):
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
            formato = col4.selectbox("Formato", ["- Seleccioná -", "Tapa Dura", "Tapa Blanda", "Bolsillo", "Revista"])
            estado = col5.selectbox("Estado", ["- Seleccioná -", "Nuevo", "Usado", "Réplica", "Antiguo"])
            ubicacion = col6.text_input("Ubicación")

            # palabras_clave = st.text_input("Palabras clave (coma)")

            col_a, col_b, col_c, col_d = st.columns(4)
            tipo_ingreso = col_a.selectbox("Tipo ingreso", ["- Seleccioná -", "Stock Heredado", "Stock Nuevo"])
            cantidad = col_b.number_input("📦 Cantidad en stock", min_value=1, max_value=100, step=1)
            precio_costo = col_c.number_input("💰 Precio unitario compra", min_value=0.0, max_value=300000.0, step=0.01, format="%.2f")
            precio_venta = col_d.number_input("🏷️ Precio unitario venta", min_value=0.0, max_value=300000.0, step=0.01, format="%.2f")

            # --- CAMPO ACTIVO: Observaciones como último ---
            observaciones = st.text_area("Observaciones")

            if st.form_submit_button("Registrar libro", type = "primary"):
                faltantes = []
            
                if not titulo.strip():
                    faltantes.append("Título")
                if categoria_id is None:
                    faltantes.append("Categoría")
                if subcategoria_id is None:
                    faltantes.append("Subcategoría")
                if autor_id is None:
                    faltantes.append("Autor principal")
                if editorial_id is None:
                    faltantes.append("Editorial")
                if formato == "- Seleccioná -":
                    faltantes.append("Formato")
                if estado == "- Seleccioná -":
                    faltantes.append("Estado")
                if cantidad is None or cantidad < 1:
                    faltantes.append("Cantidad en stock")
                if tipo_ingreso == "- Seleccioná -":
                    faltantes.append("Tipo de ingreso")
            
                if faltantes:
                    mensaje = "⚠️ Debés completar los siguientes campos obligatorios:\n\n- " + "\n- ".join(faltantes)
                    mensaje += "\n\n💡 *Ingresá los precios usando solo punto (.) para decimales. Ejemplo válido: 72500.50*"
                    st.warning(mensaje)
                    st.stop()
            
                datos_libro = limpiar_valores_nulos({
                    "titulo": titulo.strip().upper(),
                    # "autor_id": autor_id,
                    "editorial_id": editorial_id,
                    # "anio": int(anio) if anio else None,
                    # "idioma": idioma if idioma != "-Seleccioná-" else None,
                    "formato": formato if formato != "- Seleccioná -" else None,
                    "estado": estado if estado != "- Seleccioná -" else None,
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
                    
                    st.session_state["autor_selector"] = "- Seleccioná autor -"
                    st.session_state["cat"] = "- Seleccioná categoría -"
                    st.session_state["subcat"] = "- Seleccioná subcategoría -"
                    st.session_state["editorial_selector"] = "- Seleccioná editorial -"
                    st.session_state["coautores"] = []
                    st.rerun()
            
                except Exception as e:
                    st.error("❌ Error al registrar.")
                    st.exception(e)
