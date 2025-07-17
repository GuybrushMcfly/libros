import streamlit as st
from supabase import create_client
from unidecode import unidecode
import re
import pandas as pd
import os
from datetime import datetime
import numpy as np
import streamlit.components.v1 as components


# --- Conexión Supabase ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- Configuración general ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Utilidad para nombre capitalizado ---
def capitalizar_nombre(nombre):
    return " ".join([s.capitalize() if not s.isupper() else s for s in re.split(r"[\s\-\.]", nombre)])

def procesar_autor(nombre, apellido):
    nombre = nombre.strip()
    apellido = apellido.strip()
    nombre_formal = f"{apellido.upper()}, {nombre.upper()}"
    nombre_visual = f"{capitalizar_nombre(nombre)} {capitalizar_nombre(apellido)}"
    sin_tildes = unidecode(nombre_formal)
    nombre_normalizado = unidecode(f"{apellido} {nombre}").lower().strip()
    return {
        "nombre_formal": nombre_formal,
        "nombre_visual": nombre_visual,
        "sin_tildes": sin_tildes,
        "nombre_normalizado": nombre_normalizado
    }


# --- Modal para agregar autor ---
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


@st.dialog("Agregar nueva editorial")
def mostrar_modal_editorial():
    nombre = st.text_input("Nombre de la editorial").strip()

    if st.button("Guardar editorial"):
        if not nombre:
            st.warning("⚠️ El nombre no puede estar vacío.")
            return

        nombre_mayus = nombre.upper()
        
        # Buscar si ya existe (por nombre exacto en mayúsculas)
        existentes = supabase.table("editoriales").select("id").eq("nombre", nombre_mayus).execute().data
        if existentes:
            st.error("❌ Ya existe una editorial con ese nombre.")
            return

        # Insertar nueva
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


def registrar_libro():
    st.title("📘 Registrar nuevo libro")

    # --- Cargar datos ---
    autores_db = supabase.table("autores").select("id, nombre_formal, nombre_visual").order("nombre_formal").execute().data
    df_autores = pd.DataFrame(autores_db)

    categorias_db = supabase.table("categorias").select("id, nombre").order("nombre").execute().data
    df_categorias = pd.DataFrame(categorias_db)

    subcategorias_db = supabase.table("subcategorias").select("id, nombre, categoria_id").order("nombre").execute().data
    df_subcategorias = pd.DataFrame(subcategorias_db)

    editoriales_db = supabase.table("editoriales").select("id, nombre").order("nombre").execute().data
    df_editoriales = pd.DataFrame(editoriales_db) if editoriales_db else pd.DataFrame(columns=["id", "nombre"])

    # --- Selección categoría/subcategoría ---
    col_cat, col_subcat = st.columns(2)
    with col_cat:
        opciones_categorias = ["-Seleccioná-"] + df_categorias["nombre"].tolist()
        categoria_nombre = st.selectbox("Categoría", opciones_categorias, key="cat")
        categoria_id = None
        if categoria_nombre != "-Seleccioná-":
            categoria_id = df_categorias[df_categorias["nombre"] == categoria_nombre]["id"].values[0]

    with col_subcat:
        if categoria_id:
            subcats = df_subcategorias[df_subcategorias["categoria_id"] == categoria_id]
            opciones_sub = ["-Seleccioná-"] + subcats["nombre"].tolist()
        else:
            subcats = pd.DataFrame()
            opciones_sub = ["-Seleccioná-"]
        subcat_nombre = st.selectbox("Subcategoría", opciones_sub, key="subcat")
        subcategoria_id = None
        if not subcats.empty and subcat_nombre != "-Seleccioná-":
            subcategoria_id = subcats[subcats["nombre"] == subcat_nombre]["id"].values[0]

    # --- Autor y Editorial: fuera del formulario ---
    col_autor, col_editorial = st.columns(2)

    with col_autor:
        opciones_autores = ["- Seleccionar autor -"] + df_autores["nombre_formal"].tolist()
        seleccion_autor = st.selectbox("Autor", opciones_autores, key="autor_selector")
        if st.button("➕ Agregar autor"):
            st.session_state["modal_autor"] = True

    with col_editorial:
        opciones_editoriales = ["- Seleccionar editorial -"] + df_editoriales["nombre"].tolist()
        seleccion_editorial = st.selectbox("Editorial", opciones_editoriales, key="editorial_selector")
        if st.button("➕ Agregar editorial"):
            st.session_state["modal_editorial"] = True

    if st.session_state.get("modal_autor"):
        mostrar_modal_autor()
    if st.session_state.get("modal_editorial"):
        mostrar_modal_editorial()

    # --- Obtener IDs seleccionados ---
    autor_id = None
    if seleccion_autor != "- Seleccionar autor -":
        fila = df_autores[df_autores["nombre_formal"] == seleccion_autor]
        if not fila.empty:
            autor_id = fila.iloc[0]["id"]

    editorial_id = None
    if seleccion_editorial != "- Seleccionar editorial -" and not df_editoriales.empty:
        fila = df_editoriales[df_editoriales["nombre"] == seleccion_editorial]
        if not fila.empty:
            editorial_id = fila.iloc[0]["id"]

    # --- Mostrar formulario solo si todo está seleccionado ---
    mostrar_formulario = all([
        categoria_id is not None,
        subcategoria_id is not None,
        autor_id is not None,
        editorial_id is not None
    ])

    if mostrar_formulario:
        with st.form("registro_libro"):
            titulo = st.text_input("Título del libro")

            col1, col2, col3 = st.columns(3)
            with col1:
                isbn = st.text_input("ISBN")
            with col2:
                anio = st.number_input("Año de publicación", min_value=1000, max_value=2100, step=1)
            with col3:
                idioma = st.selectbox("Idioma", ["-Seleccioná-", "ESPAÑOL", "INGLÉS", "FRANCÉS", "ITALIANO", "OTRO"])

            col4, col5, col6 = st.columns(3)
            with col4:
                formato = st.selectbox("Formato", ["-Seleccioná-", "TAPA DURA", "TAPA BLANDA", "BOLSILLO", "REVISTA"])
            with col5:
                estado = st.selectbox("Estado", ["-Seleccioná-", "NUEVO", "USADO", "REPLICA", "ANTIGUO"])
            with col6:
                ubicacion = st.text_input("Ubicación en estantería")

            descripcion = st.text_area("Descripción")
            palabras_clave = st.text_input("Palabras clave (separadas por coma)")

            col_precio_costo, col_precio_venta, col_cantidad, col_tipo_ingreso = st.columns(4)
            with col_precio_costo:
                precio_costo = st.number_input("💰 Precio de compra", min_value=0.0, step=0.01)
            with col_precio_venta:
                precio_venta = st.number_input("🏷️ Precio de venta", min_value=0.0, step=0.01)
            with col_cantidad:
                cantidad = st.number_input("📦 Cantidad en stock", min_value=1, step=1)
            with col_tipo_ingreso:
                tipo_ingreso = st.selectbox("Tipo de ingreso", ["-Seleccioná-", "STOCK HEREDADO", "INGRESO NUEVO"])

            if st.form_submit_button("Registrar libro"):
                if not titulo.strip():
                    st.error("⚠️ El título del libro es obligatorio.")
                    st.stop()
                if tipo_ingreso == "-Seleccioná-":
                    st.warning("⚠️ Debés seleccionar un tipo de ingreso.")
                    st.stop()

                libro_data = {
                    "titulo": titulo.strip().upper(),
                    "autor_id": autor_id,
                    "editorial_id": editorial_id,
                    "anio": int(anio) if anio else None,
                    "idioma": idioma if idioma != "-Seleccioná-" else None,
                    "formato": formato if formato != "-Seleccioná-" else None,
                    "estado": estado if estado != "-Seleccioná-" else None,
                    "descripcion": descripcion.strip() if descripcion else None,
                    "isbn": isbn.strip() if isbn else None,
                    "ubicacion": ubicacion.strip() if ubicacion else None,
                    "palabras_clave": [p.strip() for p in palabras_clave.split(",")] if palabras_clave else None,
                    "fecha_creacion": datetime.now().isoformat(),
                    "subcategoria_id": subcategoria_id
                }

                # Limpieza
                libro_data = {
                    k: None if (
                        v is None or
                        (isinstance(v, str) and v.strip().upper() == "NULL") or
                        (isinstance(v, float) and pd.isna(v)) or
                        isinstance(v, pd._libs.missing.NAType) or
                        (isinstance(v, np.float64) and np.isnan(v))
                    ) else v
                    for k, v in libro_data.items()
                }


                try:
                    resultado = supabase.table("libros").insert(libro_data).execute()
                    if not resultado.data:
                        st.error("❌ No se insertó el libro.")
                        st.stop()

                    libro_id = resultado.data[0]["id"]

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

                    st.success("✅ Libro y stock registrados correctamente.")

                    # --- LIMPIEZA de formulario tras inserción exitosa ---
                    for key in list(st.session_state.keys()):
                        if key.startswith("libro_") or key in [
                            "titulo", "editorial", "anio", "idioma", "formato", "estado",
                            "descripcion", "isbn", "ubicacion", "palabras_clave",
                            "precio_costo", "precio_venta", "cantidad", "tipo_ingreso",
                            "autor_selector", "cat", "subcat", "editorial_selector"
                        ]:
                            del st.session_state[key]

                    st.session_state["autor_selector"] = "- Seleccionar autor -"
                    st.session_state["cat"] = "-Seleccioná-"
                    st.session_state["subcat"] = "-Seleccioná-"
                    st.session_state["editorial_selector"] = "- Seleccionar editorial -"

                    st.rerun()

                except Exception as e:
                    st.error("❌ Error al registrar el libro.")
                    st.exception(e)




# --- Página: Registrar autor (manual/independiente) ---
def registrar_autor():
    st.title("✍️ Registrar autor")

    nombre_input = st.text_input("Apellido, Nombre del autor").strip()

    def procesar_autor_desde_texto(input_texto):
        texto = input_texto.strip()
        if "," in texto:
            partes = [p.strip() for p in texto.split(",")]
            apellido = partes[0] if len(partes) >= 1 else ""
            nombre = partes[1] if len(partes) == 2 else ""
        else:
            tokens = texto.split()
            apellido = " ".join(tokens[:-1]) if len(tokens) >= 2 else texto
            nombre = tokens[-1] if len(tokens) >= 2 else ""
        return procesar_autor(nombre, apellido)

    if st.button("Ingresar autor") and nombre_input:
        datos = procesar_autor_desde_texto(nombre_input)
        supabase.table("autores").insert(datos).execute()
        st.success("✅ Autor registrado correctamente.")

# --- Funciones placeholder ---
def registrar_editorial():
    st.title("🏷️ Registrar editorial")

def registrar_proveedor():
    st.title("🏢 Registrar proveedor")

def buscar_libros():
    st.title("🔍 Buscar libros")

def buscar_ventas():
    st.title("📄 Buscar ventas")

def registrar_venta():
    st.title("💰 Registrar venta")

def historial_ventas():
    st.title("📊 Historial de ventas")

def ver_stock():
    st.title("📦 Ver stock")

    with st.spinner("🔄 Cargando datos desde Supabase..."):
        try:
            libros_data = supabase.table("libros").select("*").execute().data
            if not libros_data:
                st.warning("📚 No se encontraron libros en la tabla.")
                return

            stock_data = supabase.table("stock").select("*").execute().data
            if not stock_data:
                st.warning("📦 No se encontraron registros en la tabla 'stock'.")
                return

            editoriales_data = supabase.table("editoriales").select("id, nombre").execute().data
            if not editoriales_data:
                st.warning("🏷️ No se encontraron editoriales.")
                return

            autores_data = supabase.table("autores").select("id, nombre_formal").execute().data
            if not autores_data:
                st.warning("✍️ No se encontraron autores.")
                return

        except Exception as e:
            st.error("❌ Error al cargar datos desde Supabase.")
            st.exception(e)
            return

    # --- Convertir a DataFrames ---
    df_libros = pd.DataFrame(libros_data)
    df_stock = pd.DataFrame(stock_data)
    df_editoriales = pd.DataFrame(editoriales_data)
    df_autores = pd.DataFrame(autores_data)

    # --- Unir libros con stock y editorial ---
    df = df_libros.merge(df_stock, left_on="id", right_on="libro_id", how="left")
    df = df.merge(df_editoriales, left_on="editorial_id", right_on="id", suffixes=("", "_editorial"))

    # --- Tabla 1: Stock por editorial ---
    st.markdown("### 🏷️ Stock por editorial")
    tabla_editorial = df.groupby("nombre")["cantidad_actual"].sum().reset_index()
    tabla_editorial.columns = ["Editorial", "Total en stock"]
    tabla_editorial = tabla_editorial.sort_values("Total en stock", ascending=False)
    st.dataframe(tabla_editorial, use_container_width=True)

    st.markdown("---")

    # --- Tabla 2: Filtro por autor ---
    st.markdown("### ✍️ Libros por autor")

    opciones_autores = df_autores["nombre_formal"].dropna().sort_values().tolist()
    seleccion_autor = st.selectbox("Seleccioná un autor", ["- Seleccioná -"] + opciones_autores)

    if seleccion_autor != "- Seleccioná -":
        autor_id = df_autores[df_autores["nombre_formal"] == seleccion_autor]["id"].values[0]
        df_filtrado = df[df["autor_id"] == autor_id][[
            "titulo", "nombre", "cantidad_actual", "precio_venta_actual", "anio", "ubicacion"
        ]]
        df_filtrado.columns = ["Título", "Editorial", "Stock", "Precio venta", "Año", "Ubicación"]
        st.dataframe(df_filtrado, use_container_width=True)




def actualizar_stock():
    st.title("🛠️ Actualizar stock")

def registrar_pedido():
    st.title("📝 Registrar pedido")

def historial_pedidos():
    st.title("📋 Historial de pedidos")

# --- Menú principal ---
pages = {
    "📥 INGRESOS": [
        st.Page(registrar_libro, title="Registrar libro", icon=":material/library_add:"),
        st.Page(registrar_editorial, title="Registrar editorial", icon=":material/edit:"),
        st.Page(registrar_proveedor, title="Registrar proveedor", icon=":material/business:"),
        st.Page(registrar_autor, title="Registrar autor", icon=":material/person_add:"),
    ],
    "🔍 BÚSQUEDA": [
        st.Page(buscar_libros, title="Buscar libros", icon=":material/search:"),
        st.Page(buscar_ventas, title="Buscar ventas", icon=":material/receipt_long:"),
    ],
    "💸 VENTAS": [
        st.Page(registrar_venta, title="Registrar venta", icon=":material/point_of_sale:"),
        st.Page(historial_ventas, title="Historial de ventas", icon=":material/history:"),
    ],
    "📦 STOCK": [
        st.Page(ver_stock, title="Ver stock", icon=":material/inventory_2:"),
        st.Page(actualizar_stock, title="Actualizar stock", icon=":material/update:"),
    ],
    "📑 PEDIDOS": [
        st.Page(registrar_pedido, title="Registrar pedido", icon=":material/post_add:"),
        st.Page(historial_pedidos, title="Historial de pedidos", icon=":material/list_alt:"),
    ]
}

# --- Ejecutar navegación ---
pg = st.navigation(pages, position="top")
pg.run()
