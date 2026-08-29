-- VariMitra demo Wari corridor seed.
-- All time-sensitive rows use source = 'seed' and must never be labeled live.

-- Route segments (lookup palkhis inserted by the schema file)
insert into wari_route_segments (
  id, palkhi_id, segment_order, start_location, end_location,
  start_latitude, start_longitude, end_latitude, end_longitude,
  route_name, distance_km, route_geometry_ref
)
select
  '33333333-3333-3333-3333-333333333331'::uuid,
  p.id, 1, 'Alandi', 'Pune',
  18.6774, 73.8965, 18.5204, 73.8567,
  'Alandi to Pune', 25.0, 'seed/dnyaneshwar/alandi-pune'
from wari_palkhis p where p.name = 'Dnyaneshwar Palkhi'
on conflict (id) do nothing;

insert into wari_route_segments (
  id, palkhi_id, segment_order, start_location, end_location,
  start_latitude, start_longitude, end_latitude, end_longitude,
  route_name, distance_km, route_geometry_ref
)
select
  '33333333-3333-3333-3333-333333333332'::uuid,
  p.id, 2, 'Pune', 'Saswad',
  18.5204, 73.8567, 18.3490, 74.0310,
  'Pune to Saswad', 32.0, 'seed/dnyaneshwar/pune-saswad'
from wari_palkhis p where p.name = 'Dnyaneshwar Palkhi'
on conflict (id) do nothing;

insert into wari_route_segments (
  id, palkhi_id, segment_order, start_location, end_location,
  start_latitude, start_longitude, end_latitude, end_longitude,
  route_name, distance_km, route_geometry_ref
)
select
  '33333333-3333-3333-3333-333333333333'::uuid,
  p.id, 3, 'Saswad', 'Pandharpur',
  18.3490, 74.0310, 17.6776, 75.3340,
  'Saswad toward Pandharpur', 180.0, 'seed/dnyaneshwar/saswad-pandharpur'
from wari_palkhis p where p.name = 'Dnyaneshwar Palkhi'
on conflict (id) do nothing;

insert into wari_route_segments (
  id, palkhi_id, segment_order, start_location, end_location,
  start_latitude, start_longitude, end_latitude, end_longitude,
  route_name, distance_km, route_geometry_ref
)
select
  '33333333-3333-3333-3333-333333333341'::uuid,
  p.id, 1, 'Dehu', 'Pune',
  18.7180, 73.7660, 18.5204, 73.8567,
  'Dehu to Pune', 28.0, 'seed/tukaram/dehu-pune'
from wari_palkhis p where p.name = 'Tukaram Palkhi'
on conflict (id) do nothing;

insert into wari_route_segments (
  id, palkhi_id, segment_order, start_location, end_location,
  start_latitude, start_longitude, end_latitude, end_longitude,
  route_name, distance_km, route_geometry_ref
)
select
  '33333333-3333-3333-3333-333333333342'::uuid,
  p.id, 2, 'Pune', 'Pandharpur',
  18.5204, 73.8567, 17.6776, 75.3340,
  'Pune toward Pandharpur', 210.0, 'seed/tukaram/pune-pandharpur'
from wari_palkhis p where p.name = 'Tukaram Palkhi'
on conflict (id) do nothing;

insert into wari_schedule (
  id, wari_year, palkhi_id, schedule_date, departure_time, departure_location,
  route_segment_id, expected_arrival_time, halt_location, halt_latitude, halt_longitude,
  expected_location, expected_latitude, expected_longitude, position_status, source, verified
)
select
  '44444444-4444-4444-4444-444444444411'::uuid,
  2026, p.id, date '2026-06-15', time '06:00', 'Alandi',
  '33333333-3333-3333-3333-333333333331'::uuid, time '17:00', 'Pune',
  18.5204, 73.8567, 'Pune (scheduled halt)', 18.5204, 73.8567,
  'scheduled', 'seed', false
from wari_palkhis p where p.name = 'Dnyaneshwar Palkhi'
on conflict (wari_year, palkhi_id, schedule_date) do nothing;

insert into wari_schedule (
  id, wari_year, palkhi_id, schedule_date, departure_time, departure_location,
  route_segment_id, expected_arrival_time, halt_location, halt_latitude, halt_longitude,
  expected_location, expected_latitude, expected_longitude, position_status, source, verified
)
select
  '44444444-4444-4444-4444-444444444412'::uuid,
  2026, p.id, date '2026-06-16', time '06:00', 'Pune',
  '33333333-3333-3333-3333-333333333332'::uuid, time '16:30', 'Saswad',
  18.3490, 74.0310, 'Saswad (scheduled halt)', 18.3490, 74.0310,
  'scheduled', 'seed', false
from wari_palkhis p where p.name = 'Dnyaneshwar Palkhi'
on conflict (wari_year, palkhi_id, schedule_date) do nothing;

insert into wari_schedule (
  id, wari_year, palkhi_id, schedule_date, departure_time, departure_location,
  route_segment_id, expected_arrival_time, halt_location, halt_latitude, halt_longitude,
  expected_location, expected_latitude, expected_longitude, position_status, source, verified
)
select
  '44444444-4444-4444-4444-444444444421'::uuid,
  2026, p.id, date '2026-06-15', time '06:30', 'Dehu',
  '33333333-3333-3333-3333-333333333341'::uuid, time '17:30', 'Pune',
  18.5204, 73.8567, 'Pune (scheduled halt)', 18.5204, 73.8567,
  'scheduled', 'seed', false
from wari_palkhis p where p.name = 'Tukaram Palkhi'
on conflict (wari_year, palkhi_id, schedule_date) do nothing;

insert into wari_major_dates (id, wari_year, event_date, title, description, location, source)
values
  (
    '55555555-5555-5555-5555-555555555501',
    2026, date '2026-06-15', 'Demo corridor start',
    'Seed demo date. This is scheduled data, not a live position.',
    'Alandi / Dehu', 'seed'
  ),
  (
    '55555555-5555-5555-5555-555555555502',
    2026, date '2026-07-02', 'Ashadhi Ekadashi (demo)',
    'Placeholder major date for the demo year. Confirm against an approved calendar.',
    'Pandharpur', 'seed'
  )
on conflict (wari_year, event_date, title) do nothing;

insert into facilities (
  id, name, type, description, latitude, longitude, address, landmark, phone,
  is_active, availability, verified, source, sanitary_pads_available, female_only, child_care_available
) values
  ('a1000000-0000-0000-0000-000000000001', 'Alandi drinking water point', 'water',
   'Seed water point near the Alandi start. Demo only.', 18.6778, 73.8970,
   'Near Alandi temple approach', 'Alandi ghat', null, true, 'unknown', false, 'seed',
   null, false, false),
  ('a1000000-0000-0000-0000-000000000002', 'Pune community kitchen', 'food',
   'Seed food stall. Demo only.', 18.5210, 73.8550,
   'Shivajinagar approach', 'Near Pune halt', null, true, 'unknown', false, 'seed',
   null, false, false),
  ('a1000000-0000-0000-0000-000000000003', 'Saswad medical tent', 'medical',
   'Seed medical help point. Demo only.', 18.3502, 74.0302,
   'Saswad main road', 'Near scheduled halt', null, true, 'unknown', false, 'seed',
   null, false, false),
  ('a1000000-0000-0000-0000-000000000004', 'Pune public toilet block', 'toilet',
   'Seed toilet. Demo only.', 18.5190, 73.8580,
   'Pune halt area', 'Bus stand side', null, true, 'unknown', false, 'seed',
   null, false, false),
  ('a1000000-0000-0000-0000-000000000005', 'Pandharpur dharamshala', 'accommodation',
   'Seed accommodation. Demo only.', 17.6788, 75.3325,
   'Near Chandrabhaga', 'Temple approach', null, true, 'unknown', false, 'seed',
   null, false, false),
  ('a1000000-0000-0000-0000-000000000006', 'Pune ST stand', 'transport',
   'Seed transport point. Demo only.', 18.5280, 73.8740,
   'Pune station area', 'ST stand', null, true, 'unknown', false, 'seed',
   null, false, false),
  ('a1000000-0000-0000-0000-000000000007', 'Pune women help point', 'women_help',
   'Seed WOMEN category point: help desk, sanitary pads, female-only rest. Demo only.',
   18.5225, 73.8540, 'Pune halt, women desk', 'Women help tent', null, true, 'unknown', true, 'seed',
   true, true, true),
  ('a1000000-0000-0000-0000-000000000008', 'Pandharpur police help desk', 'police',
   'Seed police point. Demo only.', 17.6760, 75.3360,
   'Pandharpur town', 'Police chowk', null, true, 'unknown', false, 'seed',
   null, false, false),
  ('a1000000-0000-0000-0000-000000000009', 'Alandi rest area', 'rest_area',
   'Seed rest area. Demo only.', 18.6760, 73.8950,
   'Alandi approach', 'Shade tent', null, true, 'unknown', false, 'seed',
   null, false, false),
  ('a1000000-0000-0000-0000-00000000000a', 'Saswad charging point', 'charging',
   'Seed charging point. Demo only.', 18.3480, 74.0325,
   'Saswad halt', 'Volunteer desk', null, true, 'unknown', false, 'seed',
   null, false, false)
on conflict (id) do nothing;

insert into local_information (id, language, topic, question, answer, source) values
  ('b1000000-0000-0000-0000-000000000001', 'en', 'wari_location_truth',
   'Is the Wari location on the map live?',
   'Scheduled Wari positions are expected locations from the approved timetable. They are not live unless a valid live source exists.',
   'seed'),
  ('b1000000-0000-0000-0000-000000000002', 'hi', 'wari_location_truth',
   'क्या नक्शे पर वारी की जगह लाइव है?',
   'अनुसूचित वारी स्थान स्वीकृत समय-सारणी से अपेक्षित हैं। जब तक कोई मान्य लाइव स्रोत न हो, उन्हें लाइव न कहें।',
   'seed'),
  ('b1000000-0000-0000-0000-000000000003', 'mr', 'wari_location_truth',
   'नकाशावरील वारीचे स्थान लाइव्ह आहे का?',
   'नियोजित वारी स्थान मंजूर वेळापत्रकातील अपेक्षित स्थान आहे. वैध लाइव्ह स्रोत नसेल तर ते लाइव्ह म्हणू नका.',
   'seed'),
  ('b1000000-0000-0000-0000-000000000004', 'en', 'how_to_sos',
   'How does SOS work?',
   'Press the large SOS button on the home screen. You have five seconds to cancel. SOS does not use voice or the cloud to start the local emergency action.',
   'seed'),
  ('b1000000-0000-0000-0000-000000000005', 'hi', 'how_to_sos',
   'SOS कैसे काम करता है?',
   'होम स्क्रीन पर बड़े SOS बटन को दबाएँ। रद्द करने के लिए पाँच सेकंड मिलते हैं। स्थानीय आपात कार्रवाई के लिए आवाज़ या क्लाउड की ज़रूरत नहीं है।',
   'seed'),
  ('b1000000-0000-0000-0000-000000000006', 'mr', 'how_to_sos',
   'SOS कसे काम करते?',
   'मुख्य स्क्रीनवरील मोठ्या SOS बटणावर दाबा. रद्द करण्यासाठी पाच सेकंद मिळतात. स्थानिक आपत्कालीन कृतीसाठी आवाज किंवा क्लाउड लागत नाही.',
   'seed'),
  ('b1000000-0000-0000-0000-000000000007', 'en', 'how_to_voice',
   'How do I use voice?',
   'Hold the voice button, speak in Marathi, Hindi, or English, then release. The app is not always listening.',
   'seed'),
  ('b1000000-0000-0000-0000-000000000008', 'mr', 'family_link',
   'लॉगिन लागते का?',
   'सामान्य वापरासाठी लॉगिन नाही. कुटुंब जोडणी एकदा QR किंवा छोट्या कोडने होते.',
   'seed')
on conflict (id) do nothing;

insert into emergency_contacts (id, name, category, phone, latitude, longitude, location, source, verified) values
  ('c1000000-0000-0000-0000-000000000001', 'Emergency services (demo)', 'ambulance',
   '112', 18.5204, 73.8567, 'Pune corridor (seed)', 'seed', false),
  ('c1000000-0000-0000-0000-000000000002', 'Pandharpur police (demo)', 'police',
   '100', 17.6776, 75.3340, 'Pandharpur (seed)', 'seed', false)
on conflict (id) do nothing;
