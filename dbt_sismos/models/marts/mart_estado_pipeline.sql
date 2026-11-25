{{ config(materialized='view') }}

select
    max(finished_at) filter (where status = 'success')                          as ultima_ejecucion_ok,
    count(*) filter (where started_at >= now() - interval '24 hours')           as ejecuciones_24h,
    count(*) filter (where status = 'failed'
                       and started_at >= now() - interval '7 days')             as fallos_7d,
    count(*)                                                                    as ejecuciones_total
from {{ source('raw', 'pipeline_runs') }}