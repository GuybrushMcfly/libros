import streamlit as st

@st.fragment
def fragment_autor(df_autores):
    # --- Autor principal ---
    seleccion_autor = st.selectbox("Autor", ["- Seleccionar autor -"] + df_autores["nombre_formal"].tolist(), key="autor_selector")
    if st.button("➕ Agregar autor"):
        st.session_state["modal_autor"] = True

    # --- Coautores ---
    if "coautores" not in st.session_state:
        st.session_state["coautores"] = []
    st.markdown("#### Coautores")
    for i, seleccion in enumerate(st.session_state["coautores"]):
        coautor = st.selectbox(f"Coautor #{i+1}", ["- Seleccionar -"] + df_autores["nombre_formal"].tolist(), key=f"coautor_{i}")
        st.session_state["coautores"][i] = coautor
    if len(st.session_state["coautores"]) < 2:
        if st.button("➕ Registrar coautor"):
            st.session_state["coautores"].append("- Seleccionar -")
            st.rerun()

    return seleccion_autor, st.session_state["coautores"]
