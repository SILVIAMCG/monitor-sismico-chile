import time
import requests
from config import ZONA

COUNT_URL = "https://earthquake.usgs.gov/fdsnws/event/1/count"

total = 0
for year in range(2010, 2027):
    params = {
        "format": "geojson",
        "starttime": f"{year}-01-01",
        "endtime": f"{year + 1}-01-01",
        **ZONA,
    }
    r = requests.get(COUNT_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    total += data["count"]
    print(f"{year}: {data['count']:>6} eventos")
    time.sleep(1)

print(f"\nTotal: {total} eventos")
print(f"Máximo permitido por consulta: {data['maxAllowed']}")