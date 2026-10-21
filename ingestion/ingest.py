import argparse
import logging
from datetime import datetime, timedelta, timezone

import requests
from psycopg.types.json import Jsonb

from config import USGS_URL, ZONA
from db import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ingest")

UPSERT_SQL = """
insert into raw.earthquakes (event_id, payload, updated_utc)
values (%s, %s, %s)
on conflict (event_id) do update
set payload = excluded.payload,
    updated_utc = excluded.updated_utc,
    ingested_at = now()
where raw.earthquakes.updated_utc < excluded.updated_utc;
"""


#Version para las ultimas horas sin considerar historico

# def fetch_events(hours: int) -> list[dict]:
#     start = datetime.now(timezone.utc) - timedelta(hours=hours)
#     params = {
#         "format": "geojson",
#         "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
#         "orderby": "time",
#         **ZONA,
#     }
#     r = requests.get(USGS_URL, params=params, timeout=30)
#     r.raise_for_status()
#     return r.json()["features"]

def fetch_range(start: datetime, end: datetime | None = None) -> list[dict]:
    params = {
        "format": "geojson",
        "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "orderby": "time",
        **ZONA,
    }
    if end is not None:
        params["endtime"] = end.strftime("%Y-%m-%dT%H:%M:%S")

    r = requests.get(USGS_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["features"]


def fetch_events(hours: int) -> list[dict]:
    start = datetime.now(timezone.utc) - timedelta(hours=hours)
    return fetch_range(start)

def load_events(features: list[dict]) -> None:
    rows = [
        (
            f["id"],
            Jsonb(f),
            datetime.fromtimestamp(f["properties"]["updated"] / 1000, tz=timezone.utc),
        )
        for f in features
    ]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(UPSERT_SQL, rows)
        conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=2, help="ventana hacia atrás en horas")
    args = parser.parse_args()

    log.info("Descargando sismos de las últimas %s horas", args.hours)
    features = fetch_events(args.hours)
    log.info("Recibidos %s eventos", len(features))

    if features:
        load_events(features)
        log.info("Carga completada")


if __name__ == "__main__":
    main()