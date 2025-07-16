import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Librería",
    page_icon=":books:"
)

st.logo("https://www.streamlit.io/images/brand/streamlit-mark-color.svg", link="https://streamlit.io")

# --- Página: Registrar libro ---
def registrar_libro():
    st.title("📘 Registrar libro")
    st.write("Aquí irá el formulario para registrar un nuevo libro.")

# --- Página: Registrar editorial ---
def registrar_editorial():
    st.title("🏢 Registrar editorial")
    st.write("Formulario futuro para ingresar una nueva editorial.")

# --- Página: Registrar proveedor ---
def registrar_proveedor():
    st.title("🚚 Registrar proveedor")
    st.write("Formulario futuro para registrar un proveedor.")

# --- Página: Buscar libro ---
def buscar_libro():
    st.title("🔍 Buscar libro")
    st.write("Buscador de libros.")

# --- Página: Buscar editorial ---
def buscar_editorial():
    st.title("📖 Buscar editorial")
    st.write("Buscador de editoriales.")

# --- Página: Buscar proveedor ---
def buscar_proveedor():
    st.title("🏬 Buscar proveedor")
    st.write("Buscador de proveedores.")

# --- Definición de páginas por sección ---
pages = [
    # INGRESOS
    st.Page(registrar_libro, title="Registrar libro", icon=":material/library_add:", section="INGRESOS"),
    st.Page(registrar_editorial, title="Registrar editorial", icon=":material/business:", section="INGRESOS"),
    st.Page(registrar_proveedor, title="Registrar proveedor", icon=":material/local_shipping:", section="INGRESOS"),

    # BÚSQUEDA
    st.Page(buscar_libro, title="Buscar libro", icon=":material/search:", section="BUSQUEDA"),
    st.Page(buscar_editorial, title="Buscar editorial", icon=":material/menu_book:", section="BUSQUEDA"),
    st.Page(buscar_proveedor, title="Buscar proveedor", icon=":material/store:", section="BUSQUEDA"),

    # VENTAS
    st.Page(lambda: st.write("Contenido ventas > opción 1"), title="Registrar venta", icon=":material/point_of_sale:", section="VENTAS"),
    st.Page(lambda: st.write("Contenido ventas > opción 2"), title="Historial ventas", icon=":material/history:", section="VENTAS"),

    # STOCK
    st.Page(lambda: st.write("Contenido stock > opción 1"), title="Ver stock", icon=":material/inventory:", section="STOCK"),
    st.Page(lambda: st.write("Contenido stock > opción 2"), title="Movimientos", icon=":material/sync_alt:", section="STOCK"),

    # PEDIDOS
    st.Page(lambda: st.write("Contenido pedidos > opción 1"), title="Registrar pedido", icon=":material/add_shopping_cart:", section="PEDIDOS"),
    st.Page(lambda: st.write("Contenido pedidos > opción 2"), title="Seguimiento", icon=":material/track_changes:", section="PEDIDOS"),
]

# --- Menú superior ---
current_page = st.navigation(pages, position="top")

# --- Ejecutar la página seleccionada ---
current_page.run()
