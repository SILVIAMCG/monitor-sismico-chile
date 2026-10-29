# Monitor Sísmico de Chile

Pipeline de datos que captura automáticamente los sismos de la zona central de Chile desde la API del USGS, los almacena en PostgreSQL con historial desde 2010 y los transforma para alimentar un dashboard en tiempo casi real.

> **En construcción** — Fases 0 a 4 completadas. En curso: Fase 5 (transformación con dbt).

---

## ¿Qué hace?

- Consulta la API del USGS cada 10 minutos y carga los sismos nuevos o revisados.
- Mantiene un historial completo desde 2010 (3.826 eventos en la zona de estudio).
- Asigna cada sismo a su región de Chile mediante cruces espaciales con PostGIS.
- Registra cada ejecución del pipeline para monitorear su funcionamiento.

**Zona de estudio:** radio de 300 km alrededor de Santiago (incluye partes de Valparaíso, O'Higgins, Maule, Coquimbo, el mar frente a la costa y zonas de Argentina). El pipeline está parametrizado para extenderse a todo Chile cambiando solo la configuración.

---

## Arquitectura

```
USGS API (GeoJSON)
      │  cada 10 min · ventana de varias horas
      ▼
GitHub Actions (cron)
  └─ ingest.py → upsert en raw + registro en pipeline_runs
      │
      ▼
Supabase · PostgreSQL + PostGIS
  ├─ raw.earthquakes     (JSON completo de cada sismo)
  ├─ raw.regiones        (polígonos regionales)
  └─ raw.pipeline_runs   (registro de ejecuciones)
      │  dbt (en desarrollo)
      ▼
staging → marts → Dashboard (próximamente)
```

---

## Stack

| Capa | Herramienta |
|---|---|
| Lenguaje | Python 3.13 (`requests`, `psycopg`, `python-dotenv`) |
| Base de datos | Supabase: PostgreSQL + PostGIS |
| Orquestación | GitHub Actions (cron) |
| Transformación | dbt Core (`dbt-postgres`) |
| Visualización | Streamlit (próximamente) |
| Exploración | Jupyter (`ipykernel`, `pandas`) |

Todo el stack es gratuito.

---

## Estructura del repositorio

```
monitor-sismico-chile/
├── .github/workflows/pipeline.yml   # cron de ingesta
├── ingestion/
│   ├── config.py                    # zona de estudio y URL de la API
│   ├── db.py                        # conexión reutilizable a Postgres
│   ├── ingest.py                    # ingesta incremental con upsert
│   ├── backfill.py                  # carga histórica mes a mes
│   ├── cargar_regiones.py           # carga de polígonos regionales
│   ├── contar_historico.py          # conteo previo de eventos por año
│   └── test_conexion.py             # prueba de conexión a la base
├── sql/
│   ├── 01_raw_earthquakes.sql
│   ├── 02_raw_regiones.sql
│   └── 03_raw_pipeline_runs.sql
├── dbt_sismos/                      # proyecto dbt (en desarrollo)
├── data/regiones_chile.geojson
├── docs/
│   ├── exploracion.ipynb
│   └── hallazgos.md
├── requirements.txt                 # dependencias del pipeline
├── requirements-dev.txt             # dependencias de desarrollo
└── .env.example
```

---

## Modelo de datos (capa raw)

| Tabla | Contenido | Columnas principales |
|---|---|---|
| `raw.earthquakes` | Un registro por sismo | `event_id` (PK), `payload` (JSONB), `updated_utc`, `ingested_at` |
| `raw.regiones` | 16 regiones de Chile | `region_id` (código HASC), `codigo`, `nombre`, `geom` (MultiPolygon, SRID 4326, índice GiST) |
| `raw.pipeline_runs` | Una fila por ejecución | `run_id`, `started_at`, `finished_at`, `window_hours`, `events`, `status`, `error` |

---

## Decisiones técnicas

**ELT con capa raw en JSON.** Cada evento se guarda completo en una columna `jsonb`, sin interpretarlo. Así no se pierde información, se puede reprocesar sin volver a llamar a la API y la ingesta no se rompe si la API agrega campos. La limpieza y el tipado se hacen después con dbt.

**Upsert idempotente.** Los sismos se revisan después de publicados (cambian magnitud y ubicación). La carga usa `INSERT ... ON CONFLICT (event_id) DO UPDATE` y solo actualiza si el campo `updated` es más reciente. Ejecutar el pipeline varias veces sobre el mismo período no genera duplicados.

**Ventana de consulta mayor que el intervalo del cron.** El cron corre cada 10 minutos, pero cada ejecución consulta varias horas hacia atrás. Esto tolera las ejecuciones atrasadas u omitidas por GitHub Actions; el upsert absorbe el solapamiento.

**Cron desplazado del minuto cero.** Se usa `3-59/10 * * * *` en vez de `*/10` para evitar los minutos de mayor carga en GitHub Actions.

**Registro de cada ejecución.** `pipeline_runs` guarda cada corrida, haya sismos o no. Sirve para monitorear el pipeline y mantiene activa la base de datos del plan gratuito.

**Zona parametrizada.** La zona de estudio vive en `config.py` como un diccionario que se desempaqueta en la consulta. Pasar de la zona central a todo Chile no requiere modificar los scripts.

**Carga histórica tolerante a fallos.** `backfill.py` carga mes a mes; si un mes falla, lo registra y continúa. Los meses fallidos se pueden repetir sin riesgo de duplicados.

**Asignación espacial de regiones.** Los sismos no traen región, solo coordenadas. La región se asigna con un cruce espacial (`ST_Contains`) contra los polígonos regionales. Los sismos en el mar se asignarán a la región más cercana y los de Argentina se identificarán aparte.

**UTC en almacenamiento.** Todas las fechas se guardan en UTC y se convierten a `America/Santiago` solo al mostrarlas.

**Entorno reproducible.** El workflow fija el runner (`ubuntu-24.04`) y usa la serie de Python (`3.13`) en vez de un parche exacto. Las dependencias del pipeline están separadas de las de desarrollo.

**Seguridad.** Data API de Supabase desactivada, Row Level Security en todas las tablas, credenciales en `.env` local y en GitHub Secrets (nunca en el repositorio).

---

## Hallazgos sobre los datos

- **Cobertura del USGS:** fuera de EE.UU. registra bien desde magnitud ~2,5–4, por lo que faltan muchos sismos menores.
- **Dos fechas distintas por evento:** `properties.time` es cuándo ocurrió el sismo y `properties.updated` es cuándo el USGS editó el registro por última vez. Agrupar por `updated` produce conteos por año incorrectos; el análisis debe usar `time`. Se detectó al validar los conteos de la base contra el endpoint de conteo de la API.
- **Volumen histórico:** 3.826 eventos desde 2010 en la zona de estudio (unos 8 MB).
- **Polígonos simplificados:** las coordenadas tienen 2 decimales (~1 km de precisión). El área calculada para la RM es de 17.051 km² frente a ~15.400 km² oficiales (+10%). Son adecuados para asignar sismos a regiones, no para calcular superficies.
- **Sismos fuera de tierra:** una parte importante de los eventos ocurre en el mar o en Argentina, fuera de los polígonos regionales.

---

## Incidentes resueltos

**Cambio de sistema operativo en GitHub Actions.** El pipeline falló cuando `ubuntu-latest` pasó a Ubuntu 26.04, donde no había una versión preparada de Python 3.13.0. Se fijó el runner en `ubuntu-24.04` y se usó la serie `3.13`.

**Base de datos pausada por inactividad.** Supabase pausó el proyecto aunque el cron corría. La causa: el script solo se conectaba a la base cuando había sismos nuevos, y en la zona central la mayoría de las ejecuciones no recibe ninguno. Se resolvió registrando cada ejecución en `pipeline_runs`.

---

## Cómo ejecutarlo localmente

```bash
# 1. Clonar y crear el entorno
git clone https://github.com/SILVIAMCG/monitor-sismico-chile
cd monitor-sismico-chile
python -m venv .venv
source .venv/Scripts/activate        # Git Bash en Windows
pip install -r requirements-dev.txt

# 2. Configurar credenciales
cp .env.example .env                 # completar con los datos de Supabase

# 3. Crear las tablas
# Ejecutar los archivos de sql/ en orden en el SQL Editor de Supabase

# 4. Cargar datos
cd ingestion
python cargar_regiones.py            # polígonos regionales
python backfill.py                   # histórico desde 2010
python ingest.py                     # ingesta incremental (últimas 2 horas)
python ingest.py --hours 48          # ventana personalizada
```

### Variables de entorno

```
DB_HOST=       # host del Session pooler de Supabase
DB_PORT=5432
DB_NAME=postgres
DB_USER=       # postgres.<id-del-proyecto>
DB_PASSWORD=
```

---

## Avance

- [x] Fase 0 — Preparación del entorno
- [x] Fase 1 — Exploración de la API
- [x] Fase 2 — Ingesta con upsert idempotente
- [x] Fase 3 — Carga histórica y polígonos regionales
- [x] Fase 4 — Automatización con GitHub Actions
- [ ] Fase 5 — Transformación con dbt *(en curso)*
- [ ] Fase 6 — Dashboard en Streamlit
- [ ] Fase 7 — Tests, monitoreo y documentación final

### Mejoras futuras

- Ampliar la zona de estudio a todo Chile.
- Alertas por Telegram o Discord para sismos de magnitud 5 o más.
- Incorporar el CSN como segunda fuente.
- Migrar los polígonos a la capa oficial DPA de IDE Chile.

---

## Fuentes de datos

- **Sismos:** [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/fdsnws/event/1/) — API pública de eventos sísmicos (dominio público).
- **Límites regionales de Chile:** [maxfindel/chile-map-geojson](https://github.com/maxfindel/chile-map-geojson), basado en datos de [OpenStreetMap](https://www.openstreetmap.org/) y [polygons.openstreetmap.fr](http://polygons.openstreetmap.fr/).
  © Colaboradores de OpenStreetMap, disponible bajo la [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).
  Los polígonos están simplificados (precisión aproximada de 1 km) y se usan solo para asignar cada sismo a su región.
## Fuentes de datos

- **Sismos:** [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/fdsnws/event/1/) — API pública de eventos sísmicos (dominio público).

- **Límites regionales de Chile:** [maxfindel/chile-map-geojson](https://github.com/maxfindel/chile-map-geojson), basado en datos de [OpenStreetMap](https://www.openstreetmap.org/) y [polygons.openstreetmap.fr](http://polygons.openstreetmap.fr/).

© Colaboradores de OpenStreetMap, disponible bajo la [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).
Los polígonos están simplificados (precisión aproximada de 1 km) y se usan solo para asignar cada sismo a su región.

