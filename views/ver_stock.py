import streamlit as st
import pandas as pd
from modules.supabase_conn import supabase

def ver_stock():
    st.title("📦 Ver stock")

    # --- Cargar datos desde Supabase ---
    try:
        libros_data = supabase.table("libros").select("*").execute().data
        stock_data = supabase.table("stock").select("*").execute().data
        autores_data = supabase.table("autores").select("id, nombre_formal").execute().data
    except Exception as e:
        st.error("❌ Error al cargar datos desde Supabase.")
        st.exception(e)
        return

    # --- Convertir a DataFrames ---
    df_libros = pd.DataFrame(libros_data)
    df_stock = pd.DataFrame(stock_data)
    df_autores = pd.DataFrame(autores_data)

    if df_libros.empty:
        st.warning("⚠️ No hay libros cargados.")
        return

    # --- Unir libros con stock ---
    df = df_libros.merge(df_stock, left_on="id", right_on="libro_id", how="left")

    # --- Reemplazar NaN de editorial por texto visible ---
    df["editorial"] = df["editorial"].fillna("SIN EDITORIAL")

    # --- Tabla 1: Stock total por editorial ---
    st.markdown("### 🏷️ Stock por editorial")
    tabla_editorial = (
        df.groupby("editorial")["cantidad_actual"]
        .sum()
        .reset_index()
        .rename(columns={"cantidad_actual": "Total en stock"})
        .sort_values("Total en stock", ascending=False)
    )
    st.dataframe(tabla_editorial, use_container_width=True)

    st.markdown("---")

    # --- Tabla 2: Filtrar por autor ---
    st.markdown("### ✍️ Libros por autor")

    opciones_autores = df_autores["nombre_formal"].dropna().sort_values().tolist()
    seleccion_autor = st.selectbox("Seleccioná un autor", ["- Seleccioná -"] + opciones_autores)

    if seleccion_autor != "- Seleccioná -":
        autor_id = df_autores[df_autores["nombre_formal"] == seleccion_autor]["id"].values[0]
        df_filtrado = df[df["autor_id"] == autor_id][[
            "titulo", "editorial", "cantidad_actual", "precio_venta_actual", "anio", "ubicacion"
        ]]
        df_filtrado.columns = ["Título", "Editorial", "Stock", "Precio venta", "Año", "Ubicación"]
        st.dataframe(df_filtrado, use_container_width=True)
