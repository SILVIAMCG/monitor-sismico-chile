# Hallazgos clave para monitorear carga de datos

# Para datos históricos, el numero total de eventos al año en la región metropolitana

2010:   1013 eventos
2011:    189 eventos
2012:    167 eventos
2013:    108 eventos
2014:    152 eventos
2015:    608 eventos
2016:    199 eventos
2017:    312 eventos
2018:    117 eventos
2019:    128 eventos
2020:    132 eventos
2021:    155 eventos
2022:    125 eventos
2023:    115 eventos
2024:    102 eventos
2025:    113 eventos
2026:     91 eventos

Total: 3826 eventos
Máximo permitido por consulta: 20000

# Fuentes de datos
Archivo geojson convertido desde el .js de maxfindel; se eliminó un comentario de JavaScript para que fuera JSON válido

# Limitaciones de precisión
El área calculada para la RM es de 17.051 km², frente a unos 15.400 km² oficiales (+10%). La diferencia se debe a la simplificación del archivo (coordenadas con 2 decimales). Los polígonos son adecuados para asignar sismos a regiones, pero no para cálculos de superficie. Mejora futura: migrar a la capa DPA oficial de IDE Chile.