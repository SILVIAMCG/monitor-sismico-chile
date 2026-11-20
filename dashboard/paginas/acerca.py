import streamlit as st

st.header("Acerca del proyecto")
st.markdown(
    """
    Pipeline de datos que captura los sismos de la zona central de Chile desde la API
    del USGS, los almacena en PostgreSQL y los transforma con dbt para alimentar este dashboard.

    *Esta sección se completará con la arquitectura, el stack y las fuentes de datos.*
    """
)