import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote
import json

# Configuración de la página
st.set_page_config(
    page_title="Buscador de Obras BVMC",
    page_icon="📚",
    layout="wide"
)

# Título principal
st.title("📚 Buscador de Obras - Biblioteca Virtual Miguel de Cervantes")
st.markdown("Búsqueda de obras utilizando consultas SPARQL sobre los datos enlazados de la BVMC")

# URL del endpoint SPARQL
SPARQL_ENDPOINT = "http://data.cervantesvirtual.com/bvmc-lod/repositories/data"

def execute_sparql_query(query):
    """Ejecuta una consulta SPARQL y devuelve los resultados"""
    try:
        headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'query': query}
        response = requests.post(SPARQL_ENDPOINT, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en la consulta: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def format_results(results):
    """Convierte los resultados SPARQL en un DataFrame de pandas"""
    if not results or 'results' not in results or 'bindings' not in results['results']:
        return pd.DataFrame()
    
    bindings = results['results']['bindings']
    if not bindings:
        return pd.DataFrame()
    
    # Extraer los datos
    data = []
    for binding in bindings:
        row = {}
        for var, value in binding.items():
            row[var] = value.get('value', '')
        data.append(row)
    
    return pd.DataFrame(data)

# Sidebar para seleccionar tipo de búsqueda
st.sidebar.header("🔍 Tipo de Búsqueda")
search_type = st.sidebar.selectbox(
    "Selecciona el tipo de búsqueda:",
    [
        "Obras de Miguel de Cervantes",
        "Idiomas disponibles",
        "Fechas de publicación",
        "Ediciones y traducciones",
        "Roles con manifestación",
        "Entidades corporativas",
        "Consulta personalizada"
    ]
)

# Diccionario con las consultas predefinidas
queries = {
    "Obras de Miguel de Cervantes": """
        PREFIX rdac: <http://rdaregistry.info/Elements/c/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?rol ?m ?label
        WHERE {
            <http://data.cervantesvirtual.com/person/40> ?rol ?m .
            ?m a rdac:Manifestation .
            ?m rdfs:label ?label
        }
        LIMIT 20
    """,
    
    "Idiomas disponibles": """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX madsrdf: <http://www.loc.gov/mads/rdf/v1#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?language (COUNT(?manifestation) AS ?no_manifestations) ?code
        WHERE {
            ?language rdf:type madsrdf:Language .
            ?language madsrdf:code ?code .
            ?manifestation dc:language ?language 
        }
        GROUP BY ?language ?code
        ORDER BY DESC(?no_manifestations)
        LIMIT 20
    """,
    
    "Fechas de publicación": """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX time: <http://www.w3.org/2006/time#>
        PREFIX rdam: <http://rdaregistry.info/Elements/m/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?lbl (COUNT(?manifestation) AS ?no_manifestations)
        WHERE {
            ?date rdf:type time:Instant .
            ?manifestation rdam:dateOfPublication ?date .
            ?date time:inDateTime ?description .
            ?description time:year ?lbl . 
        }
        GROUP BY ?lbl
        ORDER BY DESC(?no_manifestations)
        LIMIT 20
    """,
    
    "Ediciones y traducciones": """
        PREFIX rdam: <http://rdaregistry.info/Elements/m/>
        SELECT ?m ?title
        WHERE {
            ?m rdam:workManifested <http://data.cervantesvirtual.com/work/18605> .
            ?m rdam:title ?title .
        }
        LIMIT 20
    """,
    
    "Roles con manifestación": """
        PREFIX rdau: <http://rdaregistry.info/Elements/u/>
        PREFIX rdac: <http://rdaregistry.info/Elements/c/>
        SELECT distinct ?rol
        WHERE {
            ?author ?rol ?m .
            ?m a rdac:Manifestation .
            ?author a rdac:Person
        }
        LIMIT 20
    """,
    
    "Entidades corporativas": """
        PREFIX rdac: <http://rdaregistry.info/Elements/c/>
        SELECT ?s
        WHERE {
            ?s a rdac:CorporateBody
        }
        LIMIT 20
    """
}

# Contenido principal
if search_type == "Consulta personalizada":
    st.header("🛠️ Consulta SPARQL Personalizada")
    
    # Área de texto para la consulta
    custom_query = st.text_area(
        "Escribe tu consulta SPARQL:",
        height=200,
        placeholder="Ejemplo:\nPREFIX rdac: <http://rdaregistry.info/Elements/c/>\nSELECT ?s WHERE { ?s a rdac:Work } LIMIT 10"
    )
    
    if st.button("Ejecutar consulta"):
        if custom_query.strip():
            with st.spinner("Ejecutando consulta..."):
                results = execute_sparql_query(custom_query)
                if results:
                    df = format_results(results)
                    if not df.empty:
                        st.success(f"Se encontraron {len(df)} resultados")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("No se encontraron resultados")
        else:
            st.warning("Por favor, ingresa una consulta SPARQL")

else:
    # Búsquedas predefinidas
    st.header(f"📋 {search_type}")
    
    # Mostrar descripción según el tipo de búsqueda
    descriptions = {
        "Obras de Miguel de Cervantes": "Lista las obras del autor Miguel de Cervantes Saavedra disponibles en el catálogo.",
        "Idiomas disponibles": "Muestra los idiomas ordenados por el número de manifestaciones asociadas.",
        "Fechas de publicación": "Lista las fechas de publicación del repositorio ordenadas por número de manifestaciones.",
        "Ediciones y traducciones": "Muestra las ediciones y traducciones de la obra 'El retablo de las maravillas'.",
        "Roles con manifestación": "Lista los diferentes roles que existen entre autores y manifestaciones.",
        "Entidades corporativas": "Obtiene las entidades corporativas disponibles en el repositorio."
    }
    
    if search_type in descriptions:
        st.info(descriptions[search_type])
    
    # Botón para ejecutar la búsqueda
    if st.button("🔍 Buscar", key=f"search_{search_type}"):
        query = queries.get(search_type)
        if query:
            with st.spinner("Buscando..."):
                results = execute_sparql_query(query)
                if results:
                    df = format_results(results)
                    if not df.empty:
                        st.success(f"Se encontraron {len(df)} resultados")
                        
                        # Mostrar resultados con formato mejorado
                        st.dataframe(df, use_container_width=True)
                        
                        # Opción para descargar resultados
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar resultados (CSV)",
                            data=csv,
                            file_name=f"bvmc_{search_type.lower().replace(' ', '_')}.csv",
                            mime="text/csv"
                        )
                        
                        # Mostrar estadísticas básicas
                        st.subheader("📊 Estadísticas")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total de resultados", len(df))
                        with col2:
                            st.metric("Columnas", len(df.columns))
                            
                    else:
                        st.warning("No se encontraron resultados para esta búsqueda")
                else:
                    st.error("Error al ejecutar la consulta")

# Información adicional en el sidebar
st.sidebar.markdown("---")
st.sidebar.header("ℹ️ Información")
st.sidebar.markdown("""
**Endpoint SPARQL:**
`http://data.cervantesvirtual.com/bvmc-lod/repositories/data`

**Prefijos comunes:**
- `rdac:` RDA Core
- `rdfs:` RDF Schema
- `madsrdf:` MADS/RDF
- `dc:` Dublin Core
- `time:` OWL-Time
- `rdam:` RDA Manifestation
- `rdau:` RDA Unconstrained
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Aplicación desarrollada para consultar los datos enlazados de la Biblioteca Virtual Miguel de Cervantes</p>
    <p>Más información: <a href='http://data.cervantesvirtual.com' target='_blank'>data.cervantesvirtual.com</a></p>
</div>
""", unsafe_allow_html=True)
