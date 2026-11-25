import pandas as pd
import streamlit as st

from datos import estado_pipeline, resumen_general

REPO_URL = "https://github.com/SILVIAMCG/monitor-sismico-chile"

st.header("Acerca del proyecto")

st.markdown(
    """
    Pipeline de datos de punta a punta que captura los sismos de Chile desde la API
    pública del **USGS**, los almacena en **PostgreSQL + PostGIS**, los transforma y
    prueba con **dbt**, y los muestra en este dashboard. Todo se ejecuta de forma
    automática cada 3 horas, usando solo herramientas gratuitas.
    """
)

# --- Estado del pipeline ---
estado = estado_pipeline().iloc[0]
total = resumen_general().iloc[0]["total"]

if pd.notna(estado["ultima_ejecucion_ok"]):
    ultima = (
        pd.Timestamp(estado["ultima_ejecucion_ok"])
        .tz_convert("America/Santiago")
        .strftime("%d-%m-%Y %H:%M")
    )
else:
    ultima = "Sin registros"

with st.container(border=True):
    st.subheader("Estado del pipeline")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Última ejecución exitosa", ultima)
    c2.metric("Ejecuciones (24 h)", int(estado["ejecuciones_24h"]))
    c3.metric("Fallos (7 días)", int(estado["fallos_7d"]))
    c4.metric("Sismos en la base", f"{int(total):,}".replace(",", "."))

# --- Arquitectura ---
DIAGRAMA = """
digraph {
    rankdir=LR;
    bgcolor="transparent";
    node [shape=box, style="rounded,filled", fillcolor="#1C1530", color="#3B2F5C",
          fontcolor="#E8E3F5", fontname="sans-serif", fontsize=11, margin="0.2,0.1"];
    edge [color="#A78BFA", fontcolor="#C4B5FD", fontname="sans-serif", fontsize=9];

    usgs [label="API USGS\\n(GeoJSON)"];
    gha  [label="GitHub Actions\\ncron cada 3 h"];
    raw  [label="raw\\nJSON completo"];
    stg  [label="staging\\nlimpio y tipado"];
    mart [label="marts\\nregión + agregados"];
    app  [label="Dashboard\\nStreamlit", color="#A78BFA", penwidth=2];

    subgraph cluster_db {
        label="Supabase · PostgreSQL + PostGIS";
        fontcolor="#E8E3F5"; fontname="sans-serif"; fontsize=10;
        color="#3B2F5C"; style="rounded";
        raw -> stg -> mart [label="dbt"];
    }

    usgs -> gha [label="últimas 12 h"];
    gha -> raw [label="upsert"];
    mart -> app;
}
"""

with st.container(border=True):
    st.subheader("Arquitectura")
    st.graphviz_chart(DIAGRAMA, width="stretch")

# --- Stack y decisiones ---
col_stack, col_decisiones = st.columns(2)

with col_stack, st.container(border=True):
    st.subheader("Stack")
    st.markdown(
        """
        - **Ingesta:** Python (`requests`, `psycopg`)
        - **Base de datos:** Supabase (PostgreSQL + PostGIS)
        - **Orquestación:** GitHub Actions
        - **Transformación y tests:** dbt Core
        - **Visualización:** Streamlit, pydeck, Altair
        """
    )

with col_decisiones, st.container(border=True):
    st.subheader("Decisiones técnicas")
    st.markdown(
        """
        - **ELT:** el JSON completo se guarda sin interpretar; dbt lo transforma después.
        - **Upsert idempotente:** los sismos revisados por el USGS se actualizan sin duplicarse.
        - **Asignación espacial:** cada sismo se cruza con los polígonos regionales en PostGIS.
        - **Tests de calidad:** rangos físicos, unicidad y totales que deben cuadrar.
        - **UTC al guardar,** hora de Chile solo al mostrar.
        """
    )

# --- Limitaciones ---
with st.container(border=True):
    st.subheader("Limitaciones")
    st.markdown(
        """
        - El USGS registra bien los sismos desde magnitud ~2,5–4 fuera de EE.UU.;
          muchos sismos menores no aparecen.
        - Los polígonos regionales están simplificados (~1 km de precisión), por lo que
          sirven para asignar regiones, pero no para medir superficies.
        - Los sismos frente a la costa se asignan a la región más cercana si ocurren
          a menos de 200 km.
        """
    )

# --- Fuentes ---
with st.container(border=True):
    st.subheader("Fuentes de datos")
    st.markdown(
        """
        - **Sismos:** [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/) (dominio público).
        - **Límites regionales:** [maxfindel/chile-map-geojson](https://github.com/maxfindel/chile-map-geojson),
          basado en datos de [OpenStreetMap](https://www.openstreetmap.org/).
          © Colaboradores de OpenStreetMap, licencia [ODbL](https://opendatacommons.org/licenses/odbl/).
        """
    )

st.link_button("Ver el código en GitHub", REPO_URL, type="primary")