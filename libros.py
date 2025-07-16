import streamlit as st

st.set_page_config(page_title="Librería", layout="wide")

# 📌 Menú principal con submenús (sin lógica aún)
seleccion = st.navigation(
    items={
        "INGRESOS": [
            "Registrar libro",
            "Registrar editorial",   # futuro
            "Registrar proveedor"    # futuro
        ],
        "BUSQUEDA": [
            "Buscar libro",
            "Buscar editorial",      # futuro
            "Buscar proveedor"       # futuro
        ],
        "VENTAS": [
            "opcion1",
            "opcion2"
        ],
        "STOCK": [
            "opcion1",
            "opcion2"
        ],
        "PEDIDOS": [
            "opcion1",
            "opcion2"
        ],
    },
    label="📚 Menú principal",
    position="top",  # 👈 esto activa la navegación superior
)

# Muestra la selección actual
st.markdown(f"## Página seleccionada: **{seleccion}**")
