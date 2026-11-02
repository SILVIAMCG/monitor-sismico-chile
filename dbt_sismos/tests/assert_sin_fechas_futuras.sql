select event_id, event_time_utc
from {{ ref('stg_earthquakes') }}
where event_time_utc > now() + interval '1 hour'