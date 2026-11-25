import pandas as pd
import pydeck as pdk
import streamlit as st

from datos import sismos_recientes
from estilos import color_magnitud, estilo_magnitud, leyenda_html

PERIODOS = {
    "Últimas 24 horas": 1,
    "Últimos 7 días": 7,
    "Últimos 30 días": 30,
}

UBICACIONES = {
    "tierra": "Tierra",
    "mar": "Frente a la costa",
    "oceano": "Océano",
    "extranjero": "Otro país",
}


def tiempo_transcurrido(momento):
    horas = (pd.Timestamp.now(tz="UTC") - momento).total_seconds() / 3600
    if horas < 1:
        return f"Hace {int(horas * 60)} min"
    if horas < 48:
        return f"Hace {int(horas)} h"
    return f"Hace {int(horas // 24)} días"


st.header("Sismos recientes")

periodo = st.radio("Período", list(PERIODOS.keys()), index=2, horizontal=True)

df = sismos_recientes()
df["event_time_utc"] = pd.to_datetime(df["event_time_utc"], utc=True)
limite = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=PERIODOS[periodo])
df = df[df["event_time_utc"] >= limite].copy()

if df.empty:
    st.info("No se registraron sismos en la zona durante este período.")
    st.stop()

df["hora"] = pd.to_datetime(df["event_time_local"]).dt.strftime("%d-%m-%Y %H:%M")

# --- Indicadores ---
mayor = df.loc[df["magnitude"].idxmax()]
ultimo = df.loc[df["event_time_utc"].idxmax()]

col1, col2, col3 = st.columns(3)
col1.metric("Sismos en el período", len(df), border=True)
col2.metric("Mayor magnitud", f"{mayor['magnitude']:.1f}", help=mayor["place"], border=True)
col3.metric("Último sismo", tiempo_transcurrido(ultimo["event_time_utc"]), help=ultimo["place"], border=True)

# --- Mapa ---
df["color"] = df["magnitude"].apply(color_magnitud)
df["radio"] = 2000 * 2 ** (df["magnitude"].fillna(3) - 3)

capa = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position=["longitude", "latitude"],
    get_fill_color="color",
    get_radius="radio",
    radius_min_pixels=4,
    radius_max_pixels=40,
    stroked=True,
    get_line_color=[255, 255, 255, 120],
    line_width_min_pixels=1,
    pickable=True,
)

vista = pdk.ViewState(latitude=-33.45, longitude=-70.66, zoom=5.5)

tooltip = {
    "html": (
        "<b>Magnitud {magnitude}</b><br/>"
        "{hora}<br/>"
        "{place}<br/>"
        "Profundidad: {depth_km} km · {region}"
    ),
    "style": {"backgroundColor": "#1C1530", "color": "#E8E3F5"},
}

with st.container(border=True):
    st.pydeck_chart(
        pdk.Deck(layers=[capa], initial_view_state=vista, tooltip=tooltip, map_style=None),
        height=520,
    )
    st.markdown(leyenda_html(), unsafe_allow_html=True)
    st.caption("El tamaño y el color del círculo indican la magnitud.")

# --- Tabla ---
tabla = (
    df.sort_values("event_time_utc", ascending=False)
    .assign(ubicacion=lambda d: d["ubicacion"].map(UBICACIONES))
    [["hora", "magnitude", "region", "ubicacion", "place", "depth_km", "usgs_url"]]
    .rename(columns={
        "hora": "Fecha y hora",
        "magnitude": "Magnitud",
        "region": "Región",
        "ubicacion": "Ubicación",
        "place": "Lugar (USGS)",
        "depth_km": "Profundidad (km)",
        "usgs_url": "Detalle",
    })
)

tabla_con_estilo = (
    tabla.style
    .map(estilo_magnitud, subset=["Magnitud"])
    .format({"Magnitud": "{:.1f}", "Profundidad (km)": "{:.0f}"})
)

with st.container(border=True):
    st.subheader("Últimos sismos")
    st.dataframe(
        tabla_con_estilo,
        hide_index=True,
        width="stretch",
        column_config={
            "Detalle": st.column_config.LinkColumn("Detalle", display_text="Ver en USGS"),
        },
    )