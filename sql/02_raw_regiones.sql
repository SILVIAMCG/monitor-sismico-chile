create table if not exists raw.regiones (
    region_id  text primary key,
    codigo     text not null,
    nombre     text not null,
    geom       geometry(MultiPolygon, 4326) not null,
    loaded_at  timestamptz not null default now()
);

create index if not exists regiones_geom_idx
    on raw.regiones using gist (geom);

alter table raw.regiones enable row level security;