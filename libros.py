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

def registrar_libro():
    st.title("📘 Registrar nuevo libro")

    # --- Cargar datos ---
    autores_db = supabase.table("autores").select("id, nombre_formal, nombre_visual").order("nombre_formal").execute().data
    df_autores = pd.DataFrame(autores_db)

    categorias_db = supabase.table("categorias").select("id, nombre").order("nombre").execute().data
    df_categorias = pd.DataFrame(categorias_db)

    subcategorias_db = supabase.table("subcategorias").select("id, nombre, categoria_id").order("nombre").execute().data
    df_subcategorias = pd.DataFrame(subcategorias_db)

    mostrar_formulario = all([
        categoria_id is not None,
        subcategoria_id is not None,
        autor_id is not None
    ])
    

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

    # --- Autor ---
    autor_id = None
    opciones = ["- Seleccionar autor -"] + df_autores["nombre_formal"].tolist()
    seleccion = st.selectbox("Autor", opciones, key="autor_selector")
    
    if st.button("➕ Agregar autor"):
        st.session_state["modal_autor"] = True
    
    # Línea divisoria opcional
    st.markdown("---")
    
    if st.session_state.get("modal_autor"):
        mostrar_modal_autor()

    if seleccion != "- Seleccionar autor -":
        fila = df_autores[df_autores["nombre_formal"] == seleccion]
        if not fila.empty:
            autor_id = fila.iloc[0]["id"]
    
    mostrar_formulario = all([
        categoria_id is not None,
        subcategoria_id is not None,
        autor_id is not None
    ])
    
    if mostrar_formulario:
        with st.form("registro_libro"):
            titulo = st.text_input("Título del libro")
        
            col1, col2, col3 = st.columns(3)
            with col1:
                editorial = st.text_input("Editorial")
            with col2:
                isbn = st.text_input("ISBN")
            with col3:
                anio = st.number_input("Año de publicación", min_value=1000, max_value=2100, step=1)
        
            col4, col5, col6 = st.columns(3)
            with col4:
                idioma = st.selectbox("Idioma", ["-Seleccioná-", "ESPAÑOL", "INGLÉS", "FRANCÉS", "ITALIANO", "OTRO"])
            with col5:
                formato = st.selectbox("Formato", ["-Seleccioná-", "TAPA DURA", "TAPA BLANDA", "BOLSILLO", "REVISTA"])
            with col6:
                estado = st.selectbox("Estado", ["-Seleccioná-", "NUEVO", "USADO", "REPLICA", "ANTIGUO"])
        
            descripcion = st.text_area("Descripción")
        
       #     st.markdown(f"**Categoría seleccionada:** {categoria_nombre if categoria_id else 'No seleccionada'}")
       #     st.markdown(f"**Subcategoría seleccionada:** {subcat_nombre if subcategoria_id else 'No seleccionada'}")

            col7, col8 = st.columns(2)
            with col7:
                palabras_clave = st.text_input("Palabras clave (separadas por coma)")
            with col8:
                ubicacion = st.text_input("Ubicación en estantería")
        
            # --- Fila con precios, cantidad y tipo de ingreso ---
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
                if autor_id is None:
                    st.error("⚠️ Debés seleccionar o registrar un autor.")
                    st.stop()
                if tipo_ingreso == "-Seleccioná-":
                    st.warning("⚠️ Debés seleccionar un tipo de ingreso.")
                    st.stop()
        
                libro_data = {
                    "titulo": titulo.strip().upper(),
                    "autor_id": autor_id,
                    "editorial": editorial.strip() if editorial else None,
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
        
                # --- Limpieza de valores nulos o inválidos ---
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
                    # Insertar libro
                    resultado = supabase.table("libros").insert(libro_data).execute()
                    if not resultado.data:
                        st.error("❌ No se insertó el libro.")
                        st.stop()
        
                    libro_id = resultado.data[0]["id"]
        
                    # Insertar stock
                    supabase.table("stock").insert({
                        "libro_id": libro_id,
                        "cantidad_actual": int(cantidad),
                        "precio_costo": float(precio_costo),
                        "precio_venta_actual": float(precio_venta),
                        "fecha_ultima_actualizacion": datetime.now().isoformat()
                    }).execute()
        
                    # Insertar movimiento
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
                            "autor_selector", "cat", "subcat"
                        ]:
                            del st.session_state[key]
        
                    st.session_state["autor_selector"] = "- Seleccionar autor -"
                    st.session_state["cat"] = "-Seleccioná-"
                    st.session_state["subcat"] = "-Seleccioná-"

        
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
