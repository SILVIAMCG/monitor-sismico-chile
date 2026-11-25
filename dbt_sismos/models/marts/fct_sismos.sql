with sismos as (

    select * from {{ ref('stg_earthquakes') }}

),

regiones as (

    select * from {{ ref('stg_regiones') }}

),

asignacion as (

    select
        s.event_id,
        tierra.region_id                                    as region_tierra,
        cercana.region_id                                   as region_cercana,
        ST_Distance(s.geom::geography, cercana.geom::geography) / 1000
                                                            as distancia_region_km
    from sismos s

    left join lateral (
        select r.region_id
        from regiones r
        where ST_Contains(r.geom, s.geom)
        limit 1
    ) tierra on true

    left join lateral (
        select r.region_id, r.geom
        from regiones r
        order by r.geom <-> s.geom
        limit 1
    ) cercana on true

)

select
    s.event_id,
    s.event_time_utc,
    s.event_time_utc at time zone 'America/Santiago'           as event_time_local,
    (s.event_time_utc at time zone 'America/Santiago')::date   as event_date_local,
    s.magnitude,
    s.mag_type,
    s.depth_km,
    s.latitude,
    s.longitude,
    s.place,
    s.review_status,
    s.tsunami_flag,
    s.usgs_url,

    case
        when a.region_tierra is not null       then 'tierra'
        when s.place not ilike '%chile%'       then 'extranjero'
        when a.distancia_region_km > 200       then 'oceano'
        else 'mar'
    end                                                        as ubicacion,

    case
        when a.region_tierra is not null       then a.region_tierra
        when s.place not ilike '%chile%'       then null
        when a.distancia_region_km > 200       then null
        else a.region_cercana
    end                                                        as region_id,

    case
        when a.region_tierra is not null       then 'Chile'
        when s.place not ilike '%chile%'       then trim(regexp_replace(s.place, '^.*,', ''))
        when a.distancia_region_km > 200       then null
        else 'Chile'
    end                                                        as pais,

    case
        when a.region_tierra is null
         and s.place ilike '%chile%'           then round(a.distancia_region_km::numeric, 1)
    end                                                        as distancia_costa_km,

    s.geom

from sismos s
left join asignacion a using (event_id)