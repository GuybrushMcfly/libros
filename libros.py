import streamlit as st

# --- Configuración inicial ---
st.set_page_config(layout="wide", page_title="Gestión Librería", page_icon="📚")

# --- Funciones de páginas (vacías por ahora) ---
def registrar_libro():
    st.title("📘 Registrar libro")

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
