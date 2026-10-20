create schema if not exists raw;

create table if not exists raw.earthquakes (
    event_id     text primary key,
    payload      jsonb not null,
    updated_utc  timestamptz not null,
    ingested_at  timestamptz not null default now()
);

alter table raw.earthquakes enable row level security;