import argparse
import logging
import time
from datetime import date, datetime, timezone

from ingest import fetch_range, load_events

log = logging.getLogger("backfill")


def meses(desde: date, hasta: date):
    actual = desde
    while actual < hasta:
        siguiente = date(actual.year + actual.month // 12, actual.month % 12 + 1, 1)
        yield actual, siguiente
        actual = siguiente


def a_datetime(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--desde", default="2010-01", help="mes inicial, formato AAAA-MM")
    args = parser.parse_args()

    anio, mes = map(int, args.desde.split("-"))
    desde = date(anio, mes, 1)
    hoy = date.today()
    hasta = date(hoy.year + hoy.month // 12, hoy.month % 12 + 1, 1)

    total = 0
    fallidos = []

    for inicio, fin in meses(desde, hasta):
        etiqueta = inicio.strftime("%Y-%m")
        try:
            features = fetch_range(a_datetime(inicio), a_datetime(fin))
            if features:
                load_events(features)
            total += len(features)
            log.info("%s: %s eventos", etiqueta, len(features))
        except Exception as e:
            log.error("%s: falló (%s)", etiqueta, e)
            fallidos.append(etiqueta)
        time.sleep(1)

    log.info("Total procesado: %s eventos", total)
    if fallidos:
        log.warning("Meses con error, volver a ejecutar: %s", ", ".join(fallidos))


if __name__ == "__main__":
    main()