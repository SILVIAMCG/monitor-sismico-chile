with sismos as (

    select * from {{ ref('fct_sismos') }}

),

regiones as (

    select * from {{ ref('stg_regiones') }}

)

select
    r.region_id,
    r.nombre,
    r.orden_norte_sur,
    count(s.event_id)                                                       as sismos_total,
    count(s.event_id) filter (where s.ubicacion = 'tierra')                 as en_tierra,
    count(s.event_id) filter (where s.ubicacion = 'mar')                    as frente_a_la_costa,
    count(s.event_id) filter (where s.event_time_utc >= now() - interval '30 days')
                                                                            as sismos_30d,
    max(s.magnitude)                                                        as magnitud_max,
    max(s.event_time_utc)                                                   as ultimo_sismo_utc
from regiones r
left join sismos s using (region_id)
group by r.region_id, r.nombre, r.orden_norte_sur