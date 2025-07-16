import streamlit as st
from supabase import create_client
from unidecode import unidecode
import re


@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- Configuración inicial ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Funciones de páginas (vacías por ahora) ---
def registrar_libro():
    st.title("📘 Registrar libro")

def registrar_libro():
    st.title("📘 Registrar nuevo libro")

    with st.form("registro_libro"):
        titulo = st.text_input("Título del libro")

        st.subheader("Autor")
        buscar_autor = st.text_input("Buscar autor")
        autor_existente = st.selectbox("Seleccionar autor", ["Autor 1", "Autor 2", "Autor 3"])
        agregar_nuevo = st.checkbox("Agregar nuevo autor")
        if agregar_nuevo:
            nuevo_autor = st.text_input("Nombre del nuevo autor")

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

        submitted = st.form_submit_button("Registrar libro")

        if submitted:
            st.success("✅ Libro registrado correctamente (simulado).")
            st.write("Título:", titulo)
            st.write("Autor:", nuevo_autor if agregar_nuevo else autor_existente)
            st.write("Editorial:", editorial)
            st.write("Año:", anio)
            st.write("Idioma:", idioma)
            st.write("Formato:", formato)
            st.write("Estado:", estado)
            st.write("Precio compra:", precio_costo)
            st.write("Precio venta:", precio_venta)
            st.write("Stock:", cantidad)


def registrar_autor():
    st.title("✍️ Registrar autor")

    nombre_input = st.text_input("Apellido, Nombre del autor").strip()

    if st.button("Ingresar autor") and nombre_input:
        # --- Normalizaciones ---
        nombre_formal = nombre_input.upper()
        partes = [parte.strip() for parte in nombre_formal.split(",")]
        if len(partes) == 2:
            nombre_visual = f"{partes[1].title()} {partes[0].title()}"
        else:
            nombre_visual = nombre_input.title()

        sin_tildes = unidecode(nombre_formal)
        nombre_normalizado = re.sub(r"[^A-Z]", "", sin_tildes.upper())

        # --- Buscar coincidencias ---
        result = supabase.table("autores").select("*").ilike("nombre_formal", f"%{partes[0]}%").execute()
        coincidencias = result.data if result.data else []

        if coincidencias:
            st.warning("⚠️ Se encontraron autores similares:")
            for autor in coincidencias:
                st.write(f"- {autor['nombre_formal']} ({autor['nombre_visual']})")
            if not st.button("Confirmar igualmente"):
                st.stop()

        # --- Insertar en Supabase ---
        nuevo = {
            "nombre_formal": nombre_formal,
            "nombre_visual": nombre_visual,
            "sin_tildes": sin_tildes,
            "nombre_normalizado": nombre_normalizado
        }
        supabase.table("autores").insert(nuevo).execute()
        st.success("✅ Autor registrado correctamente.")


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

# --- Menú de navegación ---
pages = {

    "📥 INGRESOS": [
        st.Page(registrar_libro, title="Registrar libro", icon=":material/library_add:"),
        st.Page(registrar_editorial, title="Registrar editorial", icon=":material/edit:"),
        st.Page(registrar_proveedor, title="Registrar proveedor", icon=":material/business:"),
        st.Page(registrar_autor, title="Registrar autor", icon=":material/person_add:"),  # nuevo
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

# --- Activar navegación ---
pg = st.navigation(pages, position="top")
pg.run()
