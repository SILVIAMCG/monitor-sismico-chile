with source as (

    select * from {{ source('raw', 'regiones') }}

),

nombres as (

    select * from {{ ref('regiones_nombres') }}

)

select
    s.region_id,
    s.codigo,
    s.nombre                                  as nombre_oficial,
    coalesce(n.nombre_corto, s.nombre)        as nombre,
    row_number() over (
        order by ST_Y(ST_Centroid(s.geom)) desc
    )                                         as orden_norte_sur,
    s.geom
from source s
left join nombres n using (region_id)