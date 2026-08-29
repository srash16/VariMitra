-- VariMitra Database v3.0
-- Supabase PostgreSQL backend; Android Room/SQLite mirrors the core tables.
create extension if not exists pgcrypto;

create table if not exists facilities (
 id uuid primary key default gen_random_uuid(),
 name text not null,
 type text not null check (type in ('water','food','medical','toilet','accommodation','transport','women_help','police','rest_area','charging')),
 description text, latitude double precision not null, longitude double precision not null,
 address text, landmark text, phone text, is_active boolean not null default true,
 availability text default 'unknown', capacity integer, current_load integer default 0,
 queue_length integer default 0, opening_time time, closing_time time,
 sanitary_pads_available boolean, female_only boolean, child_care_available boolean,
 verified boolean not null default false, source text,
 last_updated timestamptz not null default now(), created_at timestamptz not null default now()
);
create index if not exists idx_facilities_type on facilities(type);
create index if not exists idx_facilities_location on facilities(latitude,longitude);

create table if not exists facility_updates (
 id uuid primary key default gen_random_uuid(),
 facility_id uuid not null references facilities(id) on delete cascade,
 crowd_level text, queue_length integer, availability text, current_load integer,
 updated_by text, updated_at timestamptz not null default now()
);

create table if not exists wari_palkhis (
 id uuid primary key default gen_random_uuid(),
 name text not null, saint_name text, description text,
 origin_location text, destination_location text default 'Pandharpur',
 active boolean not null default true, created_at timestamptz not null default now()
);

create table if not exists wari_route_segments (
 id uuid primary key default gen_random_uuid(),
 palkhi_id uuid references wari_palkhis(id) on delete cascade,
 segment_order integer not null, start_location text not null, end_location text not null,
 start_latitude double precision, start_longitude double precision,
 end_latitude double precision, end_longitude double precision,
 route_name text, distance_km double precision, route_geometry_ref text,
 created_at timestamptz not null default now(), unique(palkhi_id,segment_order)
);

create table if not exists wari_schedule (
 id uuid primary key default gen_random_uuid(),
 wari_year integer not null, palkhi_id uuid references wari_palkhis(id) on delete cascade,
 schedule_date date not null, departure_time time, departure_location text,
 route_segment_id uuid references wari_route_segments(id),
 expected_arrival_time time, halt_location text, halt_latitude double precision,
 halt_longitude double precision, expected_location text,
 expected_latitude double precision, expected_longitude double precision,
 position_status text not null default 'scheduled'
   check(position_status in ('scheduled','live','last_known','unknown')),
 source text, verified boolean not null default false,
 last_updated timestamptz not null default now(), created_at timestamptz not null default now(),
 unique(wari_year,palkhi_id,schedule_date)
);
create index if not exists idx_wari_schedule_date on wari_schedule(wari_year,schedule_date);

create table if not exists wari_major_dates (
 id uuid primary key default gen_random_uuid(), wari_year integer not null,
 event_date date not null, title text not null, description text, location text,
 source text, last_updated timestamptz not null default now(),
 unique(wari_year,event_date,title)
);

create table if not exists local_information (
 id uuid primary key default gen_random_uuid(),
 language text not null check(language in ('mr','hi','en')),
 topic text not null, question text, answer text not null, source text,
 last_updated timestamptz not null default now()
);

create table if not exists family_links (
 id uuid primary key default gen_random_uuid(),
 pilgrim_device_id text not null, family_device_id text,
 pairing_code_hash text, qr_token_hash text, family_name text,
 emergency_contact text, is_active boolean not null default true,
 paired_at timestamptz, expires_at timestamptz, created_at timestamptz not null default now()
);
create index if not exists idx_family_pilgrim_device on family_links(pilgrim_device_id);

create table if not exists lost_person_reports (
 id uuid primary key default gen_random_uuid(),
 family_link_id uuid references family_links(id) on delete set null,
 reported_by_device_id text not null, person_name text, age integer, gender text,
 description text, last_seen_location text, latitude double precision, longitude double precision,
 photo_url text, contact_number text,
 status text not null default 'missing' check(status in ('missing','found','closed','cancelled')),
 client_created_at timestamptz, server_received_at timestamptz,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);

create table if not exists sos_alerts (
 id uuid primary key default gen_random_uuid(),
 device_id text not null, family_link_id uuid references family_links(id) on delete set null,
 latitude double precision, longitude double precision, location_name text,
 emergency_type text not null default 'general', message text,
 status text not null default 'pending'
   check(status in ('pending','acknowledged','responding','resolved','cancelled','failed')),
 emergency_action text, action_result text, client_created_at timestamptz,
 created_at timestamptz not null default now(), acknowledged_at timestamptz, resolved_at timestamptz
);

create table if not exists facility_reports (
 id uuid primary key default gen_random_uuid(),
 facility_id uuid references facilities(id) on delete set null,
 reported_by_device_id text not null, report_type text not null,
 description text, photo_url text,
 status text not null default 'pending'
   check(status in ('pending','active','resolved','cancelled')),
 created_at timestamptz not null default now(), resolved_at timestamptz
);

create table if not exists food_water_requests (
 id uuid primary key default gen_random_uuid(),
 requested_by_device_id text not null,
 type text not null check(type in ('food','water')), quantity_needed integer,
 latitude double precision, longitude double precision, location_name text,
 urgency text not null default 'medium', status text not null default 'pending'
   check(status in ('pending','active','resolved','cancelled')),
 fulfilled_by_device_id text, created_at timestamptz not null default now(), fulfilled_at timestamptz
);

create table if not exists distribution_records (
 id uuid primary key default gen_random_uuid(), volunteer_device_id text not null,
 type text not null check(type in ('food','water')), quantity integer not null,
 latitude double precision, longitude double precision, location_name text,
 request_id uuid references food_water_requests(id) on delete set null,
 status text not null default 'resolved', distributed_at timestamptz not null default now()
);

create table if not exists emergency_contacts (
 id uuid primary key default gen_random_uuid(), name text not null, category text not null,
 phone text, latitude double precision, longitude double precision, location text,
 source text, verified boolean not null default false,
 last_updated timestamptz not null default now()
);

create table if not exists sync_events (
 id uuid primary key default gen_random_uuid(), device_id text not null,
 entity_type text not null, entity_id uuid,
 operation text not null check(operation in ('insert','update','delete')),
 payload jsonb, status text not null default 'queued'
   check(status in ('queued','synced','failed')),
 retry_count integer not null default 0, error_message text,
 client_created_at timestamptz, created_at timestamptz not null default now(), synced_at timestamptz
);

insert into wari_palkhis(name,saint_name,description)
values ('Dnyaneshwar Palkhi','Sant Dnyaneshwar','Sant Dnyaneshwar Palkhi Wari route'),
       ('Tukaram Palkhi','Sant Tukaram','Sant Tukaram Palkhi Wari route')
on conflict do nothing;

create or replace view active_facilities as
select * from facilities where is_active=true;

create or replace view latest_facility_updates as
select distinct on(facility_id) facility_id,crowd_level,queue_length,availability,current_load,updated_by,updated_at
from facility_updates order by facility_id,updated_at desc;

-- IMPORTANT:
-- Map tiles/routing files and STT/LLM/TTS models are app assets, not database rows.
-- Android Room should mirror facilities, wari_palkhis, wari_route_segments,
-- wari_schedule, wari_major_dates, local_information, emergency_contacts,
-- family_links, lost_person_reports and sos_alerts, plus a LOCAL sync_queue.
