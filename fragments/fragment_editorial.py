import streamlit as st

@st.fragment
def fragment_editorial(df_editoriales):
    seleccion_editorial = st.selectbox("Editorial", ["- Seleccionar editorial -"] + df_editoriales["nombre"].tolist(), key="editorial_selector")
    if st.button("➕ Agregar editorial"):
        st.session_state["modal_editorial"] = True
    return seleccion_editorial
