with calendario as (

    select generate_series(
        date '2010-01-01',
        (now() at time zone 'America/Santiago')::date,
        interval '1 day'
    )::date as fecha

),

sismos as (

    select * from {{ ref('fct_sismos') }}
    where ubicacion in ('tierra', 'mar')

)

select
    c.fecha,
    count(s.event_id)                                       as sismos,
    count(s.event_id) filter (where s.magnitude >= 4)       as sismos_m4,
    count(s.event_id) filter (where s.magnitude >= 5)       as sismos_m5,
    max(s.magnitude)                                        as magnitud_max
from calendario c
left join sismos s on s.event_date_local = c.fecha
group by c.fecha