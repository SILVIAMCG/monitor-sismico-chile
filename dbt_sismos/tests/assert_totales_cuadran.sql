with diario as (

    select sum(sismos) as total from {{ ref('mart_actividad_diaria') }}

),

regional as (

    select sum(sismos_total) as total from {{ ref('mart_resumen_regional') }}

)

select
    diario.total   as total_diario,
    regional.total as total_regional
from diario, regional
where diario.total <> regional.total