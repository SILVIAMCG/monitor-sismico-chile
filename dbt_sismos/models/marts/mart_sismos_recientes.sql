{{ config(materialized='view') }}

with sismos as (

    select * from {{ ref('fct_sismos') }}

),

regiones as (

    select * from {{ ref('stg_regiones') }}

)

select
    s.event_id,
    s.event_time_utc,
    s.event_time_local,
    s.magnitude,
    s.depth_km,
    s.latitude,
    s.longitude,
    s.place,
    s.ubicacion,
    coalesce(r.nombre, 'Argentina')     as region,
    s.distancia_costa_km,
    s.usgs_url
from sismos s
left join regiones r using (region_id)
where s.event_time_utc >= now() - interval '30 days'