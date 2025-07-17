import streamlit as st
from supabase import create_client
from unidecode import unidecode
import re
import pandas as pd
import os

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

# --- Página: Registrar libro ---
def registrar_libro():
    st.title("📘 Registrar nuevo libro")

    autores_db = supabase.table("autores").select("id, nombre_formal, nombre_visual").order("nombre_formal").execute().data
    df_autores = pd.DataFrame(autores_db)

    autor_id = None

    col1, col2 = st.columns([4, 1])
    with col1:
        opciones = ["- Seleccionar autor -"] + df_autores["nombre_visual"].tolist()
        seleccion = st.selectbox("Autor", opciones, key="autor_selector")
    with col2:
        if st.button("➕ Agregar"):
            st.session_state["modal_autor"] = True

    if st.session_state.get("modal_autor"):
        mostrar_modal_autor()

    if seleccion != "- Seleccionar autor -":
        # Buscar por nombre_visual
        fila = df_autores[df_autores["nombre_formal"] == seleccion]
        if not fila.empty:
            autor_id = fila.iloc[0]["id"]
            st.info(f"Autor seleccionado: ID {autor_id}")

        with st.form("registro_libro"):
            titulo = st.text_input("Título del libro")
            editorial = st.text_input("Editorial")
            anio = st.number_input("Año de publicación", min_value=1000, max_value=2100, step=1)
            idioma = st.selectbox("Idioma", ["ESPAÑOL", "INGLÉS", "FRANCÉS", "ITALIANO", "OTRO"])
            formato = st.selectbox("Formato", ["TAPA DURA", "TAPA BLANDA", "BOLSILLO", "REVISTA"])
            estado = st.selectbox("Estado", ["NUEVO", "USADO", "REPLICA", "ANTIGUO"])
            descripcion = st.text_area("Descripción")
            isbn = st.text_input("ISBN")
            palabras_clave = st.text_input("Palabras clave (separadas por coma)")
            ubicacion = st.text_input("Ubicación en estantería")
            precio_costo = st.number_input("Precio de compra", min_value=0.0, step=0.01)
            precio_venta = st.number_input("Precio de venta sugerido", min_value=0.0, step=0.01)
            cantidad = st.number_input("Cantidad en stock", min_value=1, step=1)

            if st.form_submit_button("Registrar libro"):
                st.success("✅ Libro registrado correctamente (simulado).")
                st.write("Título:", titulo)
                st.write("Autor ID:", autor_id)
                st.write("Editorial:", editorial)
                st.write("Año:", anio)
                st.write("Idioma:", idioma)
                st.write("Formato:", formato)
                st.write("Estado:", estado)
                st.write("Precio compra:", precio_costo)
                st.write("Precio venta:", precio_venta)
                st.write("Stock:", cantidad)

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
