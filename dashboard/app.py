import streamlit as st

st.set_page_config(
    page_title="Monitor Sísmico de Chile",
    page_icon="🌎",
    layout="wide",
)

st.title("🌎 Monitor Sísmico de Chile")
st.caption("Chile · Datos del USGS, actualizados cada 3 horas")

paginas = [
    st.Page("paginas/monitor.py", title="Monitor", icon="🗺️", default=True),
    st.Page("paginas/historico.py", title="Histórico", icon="📈"),
    st.Page("paginas/acerca.py", title="Acerca del proyecto", icon="ℹ️"),
]

st.navigation(paginas).run()