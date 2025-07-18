import streamlit as st
from modules.supabase_conn import supabase
import pandas as pd

# --- Cargar y cachear lista de autores ---
@st.cache_data(ttl=3600)
def cargar_autores():
    autores_data = supabase.table("autores").select("id, nombre_formal").order("nombre_formal").execute().data
    return pd.DataFrame(autores_data)

def buscar_libros():
    st.title("🔎 Buscar libros")

    # --- Selector de tipo de búsqueda ---
    tipo_busqueda = st.radio(
        "Buscar por:", 
        options=["Autor", "Título (próximamente)", "Editorial (próximamente)"], 
        horizontal=True
    )

    if tipo_busqueda == "Autor":
        # --- Dropdown de autores cacheado ---
        df_autores = cargar_autores()
        lista_autores = ["- Seleccioná autor -"] + df_autores["nombre_formal"].tolist()
        autor_seleccionado = st.selectbox("Autor", lista_autores)

        # --- Buscar libros solo si se selecciona autor válido ---
        if autor_seleccionado != "- Seleccioná autor -":
            # Buscar el id del autor seleccionado
            autor_id = df_autores[df_autores["nombre_formal"] == autor_seleccionado]["id"].iloc[0]
            
            # 1. Obtener los libros de ese autor desde la tabla libros_autores
            libros_autores = supabase.table("libros_autores").select("libro_id").eq("autor_id", autor_id).execute().data
            libro_ids = [la["libro_id"] for la in libros_autores]

            if libro_ids:
                # 2. Traer datos de libros por esos ids
                libros_data = supabase.table("libros").select("id, titulo").in_("id", libro_ids).execute().data
                df_libros = pd.DataFrame(libros_data)

                # 3. Traer stock y precio para esos libros
                stock_data = supabase.table("stock").select("libro_id, cantidad_actual, precio_venta_actual").in_("libro_id", libro_ids).execute().data
                df_stock = pd.DataFrame(stock_data)

                # 4. Traer coautores para esos libros
                coautores_data = supabase.table("libros_autores").select("libro_id, autor_id").in_("libro_id", libro_ids).execute().data
                df_coautores = pd.DataFrame(coautores_data)
                df_coautores = df_coautores.merge(df_autores, left_on="autor_id", right_on="id", how="left")

                # Construir la columna de autores para cada libro
                autores_por_libro = df_coautores.groupby("libro_id")["nombre_formal"].apply(lambda nombres: " / ".join(nombres)).reset_index()
                
                # Armar la tabla final para mostrar
                df_final = df_libros.merge(autores_por_libro, left_on="id", right_on="libro_id", how="left")
                df_final = df_final.merge(df_stock, left_on="id", right_on="libro_id", how="left")

                # Solo mostrar las columnas requeridas
                df_final = df_final[["nombre_formal", "titulo", "cantidad_actual", "precio_venta_actual"]]
                df_final.columns = ["Autor(es)", "Título", "Cantidad en stock", "Precio de venta"]

                st.write("### Resultados")
                st.dataframe(df_final, use_container_width=True)
            else:
                st.info("No se encontraron libros para el autor seleccionado.")
        else:
            st.info("Seleccioná un autor para buscar libros.")
    else:
        st.info("Funcionalidad disponible próximamente.")

# --- Si esto es un archivo views/buscar_libros.py, solo dejá esta función pública ---
if __name__ == "__main__":
    buscar_libros()

