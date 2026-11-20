import streamlit as st

TTL = 1800  # segundos; coincide con la frecuencia del pipeline


def conexion():
    return st.connection("sismos", type="sql")


def resumen_general():
    return conexion().query(
        """
        select
            count(*)              as total,
            max(magnitude)        as magnitud_max,
            max(event_time_local) as ultimo_sismo
        from marts.fct_sismos
        where ubicacion in ('tierra', 'mar')
        """,
        ttl=TTL,
    )


def actividad_mensual():
    return conexion().query(
        """
        select
            date_trunc('month', fecha)::date as mes,
            sum(sismos)                      as sismos,
            sum(sismos_m5)                   as sismos_m5
        from marts.mart_actividad_diaria
        group by 1
        order by 1
        """,
        ttl=TTL,
    )

def sismos_recientes():
    return conexion().query(
        """
        select
            event_id,
            event_time_utc,
            event_time_local,
            magnitude,
            depth_km,
            latitude,
            longitude,
            place,
            region,
            ubicacion,
            usgs_url
        from marts.mart_sismos_recientes
        order by event_time_utc desc
        """,
        ttl=TTL,
    )

def resumen_regional():
    return conexion().query(
        """
        select nombre, orden_norte_sur, sismos_total, en_tierra,
               frente_a_la_costa, sismos_30d, magnitud_max
        from marts.mart_resumen_regional
        where sismos_total > 0
        order by orden_norte_sur
        """,
        ttl=TTL,
    )


def mayores_sismos():
    return conexion().query(
        """
        select
            f.event_time_local,
            f.magnitude,
            coalesce(r.nombre, 'Argentina') as region,
            f.ubicacion,
            f.place,
            f.depth_km,
            f.usgs_url
        from marts.fct_sismos f
        left join staging.stg_regiones r using (region_id)
        where f.ubicacion in ('tierra', 'mar')
        order by f.magnitude desc, f.event_time_utc desc
        limit 10
        """,
        ttl=TTL,
    )