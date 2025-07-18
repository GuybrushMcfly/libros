import streamlit as st
from modules.supabase_conn import supabase
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

@st.cache_data(ttl=3600)
def cargar_autores():
    autores_data = supabase.table("autores").select("id, nombre_formal").order("nombre_formal").execute().data
    return pd.DataFrame(autores_data)

def buscar_libros():
    st.title("🔎 Buscar libros")

    tipo_busqueda = st.radio(
        "Buscar por:", 
        options=["Autor", "Título (próximamente)", "Editorial (próximamente)"], 
        horizontal=True
    )

    if tipo_busqueda == "Autor":
        df_autores = cargar_autores()
        lista_autores = ["- Seleccioná autor -"] + df_autores["nombre_formal"].tolist()
        autor_seleccionado = st.selectbox("Autor", lista_autores)

        if autor_seleccionado != "- Seleccioná autor -":
            autor_id = df_autores[df_autores["nombre_formal"] == autor_seleccionado]["id"].iloc[0]
            libros_autores = supabase.table("libros_autores").select("libro_id").eq("autor_id", autor_id).execute().data
            libro_ids = [la["libro_id"] for la in libros_autores]

            if libro_ids:
                # 1. Traer info de libros
                libros_data = supabase.table("libros").select(
                    "id, titulo, editorial_id, ubicacion, formato, estado, anio, isbn, idioma"
                ).in_("id", libro_ids).execute().data
                df_libros = pd.DataFrame(libros_data)

                # 2. Stock y precio
                stock_data = supabase.table("stock").select("libro_id, cantidad_actual, precio_venta_actual").in_("libro_id", libro_ids).execute().data
                df_stock = pd.DataFrame(stock_data)

                # 3. Coautores (trae todos)
                coautores_data = supabase.table("libros_autores").select("libro_id, autor_id").in_("libro_id", libro_ids).execute().data
                df_coautores = pd.DataFrame(coautores_data)
                df_coautores = df_coautores.merge(df_autores, left_on="autor_id", right_on="id", how="left")

                autores_por_libro = df_coautores.groupby("libro_id")["nombre_formal"].apply(lambda nombres: " / ".join(nombres)).reset_index()

                # Merge tabla base
                df_base = df_libros.merge(autores_por_libro, left_on="id", right_on="libro_id", how="left")
                df_base = df_base.merge(df_stock, left_on="id", right_on="libro_id", how="left")

                # Tabla para AgGrid, agregando id como columna oculta
                df_aggrid = df_base[["id", "nombre_formal", "titulo", "cantidad_actual", "precio_venta_actual"]].copy()
                df_aggrid.columns = ["ID", "Autor(es)", "Título", "Cantidad en stock", "Precio de venta"]

                st.write("### Resultados")
                gb = GridOptionsBuilder.from_dataframe(df_aggrid)
                gb.configure_selection(selection_mode="single", use_checkbox=False)
                gb.configure_column("ID", hide=True)  # Oculta la columna ID en la grilla
                grid_options = gb.build()

                grid_response = AgGrid(
                    df_aggrid,
                    gridOptions=grid_options,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    enable_enterprise_modules=False,
                    allow_unsafe_jscode=True,
                    theme="streamlit",
                    fit_columns_on_grid_load=True,
                    height=300
                )

                selected_rows = grid_response["selected_rows"]
                
                # Si es un DataFrame, convertí a lista de dicts
                if isinstance(selected_rows, pd.DataFrame):
                    selected_rows = selected_rows.to_dict(orient="records")
                
                if selected_rows is not None and len(selected_rows) > 0:
                    seleccion = selected_rows[0]
                    libro_id = seleccion["ID"]

                    # Buscar el libro correspondiente por ID
                    fila_libro = df_base[df_base["id"] == libro_id].iloc[0]

                    # Buscar editorial (nombre)
                    editorial_nombre = "-"
                    if pd.notnull(fila_libro.get("editorial_id", None)):
                        editorial_row = supabase.table("editoriales").select("nombre").eq("id", fila_libro["editorial_id"]).execute().data
                        if editorial_row:
                            editorial_nombre = editorial_row[0]["nombre"]

                    # --- Card visual para detalles del libro seleccionado ---
                    st.markdown(
                        f"""
                        <div style="border-radius: 18px; border: 1px solid #e0e0e0; background-color: #f7f7fc; padding: 1.5em 1em; box-shadow: 0 2px 8px rgba(180,180,220,0.08); margin-bottom: 1em;">
                            <h2 style="margin-top: 0; font-size: 1.4em;">📚 <b>{fila_libro['titulo']}</b></h2>
                            <p style="margin-bottom: 8px; font-size: 1.1em;">👤 <b>Autor(es):</b> {fila_libro['nombre_formal']}</p>
                            <p style="margin-bottom: 8px;">🏷️ <b>Editorial:</b> {editorial_nombre}</p>
                            <p style="margin-bottom: 8px;">💲 <b>Precio de venta:</b> ${fila_libro['precio_venta_actual']}</p>
                            <p style="margin-bottom: 12px;">📦 <b>Stock:</b> {fila_libro['cantidad_actual']}</p>
                            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 1em 0;">
                            <p style="margin-bottom: 6px;">🏠 <b>Ubicación:</b> {fila_libro['ubicacion'] or '-'}</p>
                            <p style="margin-bottom: 6px;">📘 <b>Formato:</b> {fila_libro['formato'] or '-'}</p>
                            <p style="margin-bottom: 6px;">⭐ <b>Estado:</b> {fila_libro['estado'] or '-'}</p>
                            <p style="margin-bottom: 6px;">🗓️ <b>Año:</b> {fila_libro['anio'] or '-'}</p>
                            <p style="margin-bottom: 6px;">🔢 <b>ISBN:</b> {fila_libro['isbn'] or '-'}</p>
                            <p style="margin-bottom: 0;">🌐 <b>Idioma:</b> {fila_libro['idioma'] or '-'}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.info("Seleccioná un libro de la tabla para ver detalles.")
            else:
                st.info("No se encontraron libros para el autor seleccionado.")
        else:
            st.info("Seleccioná un autor para buscar libros.")
    else:
        st.info("Funcionalidad disponible próximamente.")

# --- Si esto es un archivo views/buscar_libros.py ---
if __name__ == "__main__":
    buscar_libros()
