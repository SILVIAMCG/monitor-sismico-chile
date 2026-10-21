# Monitor Sísmico de Chile

Pipeline de datos que captura los sismos de Chile desde la API del USGS
cada 10 minutos, los almacena en PostgreSQL y los muestra en un dashboard en vivo.

## Estado
En construcción — Fase 1: exploración de la API.

## Stack
Python · PostgreSQL/PostGIS (Supabase) · dbt · GitHub Actions · Streamlit

## Fuentes de datos

- **Sismos:** [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/fdsnws/event/1/) — API pública de eventos sísmicos (dominio público).

- **Límites regionales de Chile:** [maxfindel/chile-map-geojson](https://github.com/maxfindel/chile-map-geojson), basado en datos de [OpenStreetMap](https://www.openstreetmap.org/) y [polygons.openstreetmap.fr](http://polygons.openstreetmap.fr/).

© Colaboradores de OpenStreetMap, disponible bajo la [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).
Los polígonos están simplificados (precisión aproximada de 1 km) y se usan solo para asignar cada sismo a su región.