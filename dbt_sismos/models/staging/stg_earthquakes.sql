with source as (

    select * from {{ source('raw', 'earthquakes') }}

),

renamed as (

    select
        event_id,

        -- fechas
        to_timestamp((payload->'properties'->>'time')::bigint / 1000.0) as event_time_utc,
        updated_utc,
        ingested_at,

        -- medición
        (payload->'properties'->>'mag')::numeric        as magnitude,
        payload->'properties'->>'magType'               as mag_type,
        (payload->'geometry'->'coordinates'->>2)::numeric as depth_km,

        -- ubicación
        (payload->'geometry'->'coordinates'->>1)::double precision as latitude,
        (payload->'geometry'->'coordinates'->>0)::double precision as longitude,
        payload->'properties'->>'place'                 as place,

        -- clasificación
        payload->'properties'->>'type'                  as event_type,
        payload->'properties'->>'status'                as review_status,
        (payload->'properties'->>'tsunami')::int = 1    as tsunami_flag,
        payload->'properties'->>'url'                   as usgs_url

    from source

)

select
    *,
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) as geom
from renamed