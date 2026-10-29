create table if not exists raw.pipeline_runs (
    run_id       bigint generated always as identity primary key,
    started_at   timestamptz not null default now(),
    finished_at  timestamptz,
    window_hours int,
    events       int,
    status       text not null,
    error        text
);

alter table raw.pipeline_runs enable row level security;