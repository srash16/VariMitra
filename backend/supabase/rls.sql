-- VariMitra RLS v3.0
-- Catalog tables are readable by anon/authenticated.
-- Pairing hashes and queued writes are not client-writable; FastAPI uses a
-- privileged role (Supabase service_role, or the local superuser) which
-- bypasses RLS.

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then
    create role anon nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then
    create role authenticated nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then
    create role service_role nologin bypassrls;
  end if;
end
$$;

grant usage on schema public to anon, authenticated, service_role;

-- Catalog: read-only for clients
do $$
declare
  catalog_table text;
begin
  foreach catalog_table in array array[
    'facilities',
    'facility_updates',
    'wari_palkhis',
    'wari_route_segments',
    'wari_schedule',
    'wari_major_dates',
    'local_information',
    'emergency_contacts'
  ]
  loop
    execute format('alter table %I enable row level security', catalog_table);
    execute format('drop policy if exists %I on %I', catalog_table || '_select_public', catalog_table);
    execute format(
      'create policy %I on %I for select to anon, authenticated using (true)',
      catalog_table || '_select_public',
      catalog_table
    );
    execute format('grant select on table %I to anon, authenticated, service_role', catalog_table);
  end loop;
end
$$;

grant select on table active_facilities to anon, authenticated, service_role;
grant select on table latest_facility_updates to anon, authenticated, service_role;

-- Sensitive / write-path tables: RLS on, no client write policies.
-- service_role bypasses RLS; local FastAPI uses the database owner.
do $$
declare
  write_table text;
begin
  foreach write_table in array array[
    'family_links',
    'lost_person_reports',
    'sos_alerts',
    'facility_reports',
    'food_water_requests',
    'distribution_records',
    'sync_events'
  ]
  loop
    execute format('alter table %I enable row level security', write_table);
    execute format('revoke all on table %I from anon, authenticated', write_table);
    execute format('grant all on table %I to service_role', write_table);
  end loop;
end
$$;
