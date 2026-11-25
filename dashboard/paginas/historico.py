import altair as alt
import streamlit as st

from datos import actividad_mensual, mayores_sismos, resumen_general, resumen_regional
from estilos import COLOR_MAR, COLOR_TIERRA, estilo_magnitud

st.header("Histórico desde 2010")

fila = resumen_general().iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Sismos registrados desde 2010", f"{int(fila['total']):,}".replace(",", "."), border=True)
col2.metric("Magnitud máxima", f"{fila['magnitud_max']:.1f}", border=True)
col3.metric("Último sismo", fila["ultimo_sismo"].strftime("%d-%m-%Y %H:%M"), border=True)

st.divider()
#se envuelve en contenedor para que tenga borde
with st.container(border=True):
    st.subheader("Actividad sísmica mensual")

    mensual = actividad_mensual()

    opcion = st.radio(
        "Mostrar",
        ["Todos los sismos", "Magnitud 5 o más"],
        horizontal=True,
    )
    columna = "sismos" if opcion == "Todos los sismos" else "sismos_m5"

    st.bar_chart(mensual, x="mes", y=columna, x_label="", y_label="Sismos por mes")

    st.caption(
        "Los picos corresponden principalmente al terremoto del Maule (27F, 2010), "
        "Iquique (2014) e Illapel (2015) y sus réplicas."
    )

# --- Ranking regional ---
regional = resumen_regional()

datos_grafico = regional.melt(
    id_vars=["nombre"],
    value_vars=["en_tierra", "frente_a_la_costa"],
    var_name="ubicacion",
    value_name="sismos",
)
datos_grafico["ubicacion"] = datos_grafico["ubicacion"].map({
    "en_tierra": "Tierra",
    "frente_a_la_costa": "Frente a la costa",
})

orden_regiones = regional["nombre"].tolist()

grafico_regiones = (
    alt.Chart(datos_grafico)
    .mark_bar(cornerRadiusEnd=3)
    .encode(
        x=alt.X("sismos:Q", title="Sismos desde 2010", stack="zero"),
        y=alt.Y("nombre:N", sort=orden_regiones, title=None),
        color=alt.Color(
            "ubicacion:N",
            title=None,
            scale=alt.Scale(
                domain=["Tierra", "Frente a la costa"],
                range=[COLOR_TIERRA, COLOR_MAR],
            ),
            legend=alt.Legend(orient="top"),
        ),
        tooltip=[
            alt.Tooltip("nombre:N", title="Región"),
            alt.Tooltip("ubicacion:N", title="Ubicación"),
            alt.Tooltip("sismos:Q", title="Sismos"),
        ],
    )
    .properties(height=480)
)

with st.container(border=True):
    st.subheader("Sismos por región")
    col_grafico, col_tabla = st.columns([3, 2])

    with col_grafico:
        st.altair_chart(grafico_regiones, width="stretch")

    with col_tabla:
        st.dataframe(
            regional[["nombre", "sismos_total", "sismos_30d", "magnitud_max"]],
            hide_index=True,
            width="stretch",
            column_config={
                "nombre": "Región",
                "sismos_total": st.column_config.NumberColumn("Total", format="%d"),
                "sismos_30d": st.column_config.NumberColumn("Últimos 30 días", format="%d"),
                "magnitud_max": st.column_config.NumberColumn("Mag. máx.", format="%.1f"),
            },
        )

    st.caption(
        "Los sismos frente a la costa se asignan a la región más cercana. "
        "No incluye los sismos ocurridos en Argentina."
    )

# --- Ranking regional ---
regional = resumen_regional()

datos_grafico = regional.melt(
    id_vars=["nombre"],
    value_vars=["en_tierra", "frente_a_la_costa"],
    var_name="ubicacion",
    value_name="sismos",
)
datos_grafico["ubicacion"] = datos_grafico["ubicacion"].map({
    "en_tierra": "Tierra",
    "frente_a_la_costa": "Frente a la costa",
})

orden_regiones = regional["nombre"].tolist()

grafico_regiones = (
    alt.Chart(datos_grafico)
    .mark_bar(cornerRadiusEnd=3)
    .encode(
        x=alt.X("sismos:Q", title="Sismos desde 2010", stack="zero"),
        y=alt.Y("nombre:N", sort=orden_regiones, title=None),
        color=alt.Color(
            "ubicacion:N",
            title=None,
            scale=alt.Scale(
                domain=["Tierra", "Frente a la costa"],
                range=[COLOR_TIERRA, COLOR_MAR],
            ),
            legend=alt.Legend(orient="top"),
        ),
        tooltip=[
            alt.Tooltip("nombre:N", title="Región"),
            alt.Tooltip("ubicacion:N", title="Ubicación"),
            alt.Tooltip("sismos:Q", title="Sismos"),
        ],
    )
    .properties(height=480)
)

with st.container(border=True):
    st.subheader("Sismos por región")
    col_grafico, col_tabla = st.columns([3, 2])

    with col_grafico:
        st.altair_chart(grafico_regiones, width="stretch")

    with col_tabla:
        st.dataframe(
            regional[["nombre", "sismos_total", "sismos_30d", "magnitud_max"]],
            hide_index=True,
            width="stretch",
            column_config={
                "nombre": "Región",
                "sismos_total": st.column_config.NumberColumn("Total", format="%d"),
                "sismos_30d": st.column_config.NumberColumn("Últimos 30 días", format="%d"),
                "magnitud_max": st.column_config.NumberColumn("Mag. máx.", format="%.1f"),
            },
        )

    st.caption(
        "Los sismos frente a la costa (hasta 200 km) se asignan a la región más cercana. "
        "No incluye los sismos en el océano abierto ni en países vecinos."
    )

# --- Mayores sismos ---
mayores = mayores_sismos()
mayores["fecha"] = mayores["event_time_local"].dt.strftime("%d-%m-%Y")
mayores["ubicacion"] = mayores["ubicacion"].map({"tierra": "Tierra", "mar": "Frente a la costa"})

tabla_mayores = (
    mayores[["fecha", "magnitude", "region", "ubicacion", "place", "depth_km", "usgs_url"]]
    .rename(columns={
        "fecha": "Fecha",
        "magnitude": "Magnitud",
        "region": "Región",
        "ubicacion": "Ubicación",
        "place": "Lugar (USGS)",
        "depth_km": "Profundidad (km)",
        "usgs_url": "Detalle",
    })
    .style
    .map(estilo_magnitud, subset=["Magnitud"])
    .format({"Magnitud": "{:.1f}", "Profundidad (km)": "{:.0f}"})
)

with st.container(border=True):
    st.subheader("Los 10 mayores sismos desde 2010")
    st.dataframe(
        tabla_mayores,
        hide_index=True,
        width="stretch",
        height=480,
        column_config={
            "Detalle": st.column_config.LinkColumn("Detalle", display_text="Ver en USGS"),
        },
    )