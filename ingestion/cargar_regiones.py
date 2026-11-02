import json
import logging
from pathlib import Path

from db import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("regiones")

RUTA = Path(__file__).resolve().parent.parent / "data" / "regiones_chile.geojson"

# Regiones cuyo código HASC viene incompleto en el archivo original.
CORRECCIONES_ID = {
    "Arica y Parinacota": "CL.AP",
}

UPSERT_SQL = """
insert into raw.regiones (region_id, codigo, nombre, geom)
values (
    %s, %s, %s,
    ST_Multi(ST_CollectionExtract(ST_MakeValid(
        ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
    ), 3))
)
on conflict (region_id) do update
set codigo    = excluded.codigo,
    nombre    = excluded.nombre,
    geom      = excluded.geom,
    loaded_at = now();
"""


def main():
    with open(RUTA, encoding="utf-8") as f:
        regiones = json.load(f)

    rows = []
    for feature in regiones["features"]:
        p = feature["properties"]

        region_id = p["hasc"]
        if not region_id or region_id.endswith("."):
            region_id = CORRECCIONES_ID.get(p["name"])
            if region_id is None:
                raise ValueError(f"Región sin código válido: {p['name']}")

        rows.append((
            region_id,
            p["hc-a2"],
            p["name"],
            json.dumps(feature["geometry"]),
        ))

    if len(rows) != 16:
        log.warning("Se esperaban 16 regiones y hay %s", len(rows))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(UPSERT_SQL, rows)
        conn.commit()

    log.info("Cargadas %s regiones", len(rows))


if __name__ == "__main__":
    main()