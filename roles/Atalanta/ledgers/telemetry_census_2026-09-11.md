# Atalanta telemetry census (raw rows for ATALANTA-04)

Regenerate: `EW_DB_HOST=<m1> python roles/Atalanta/ledgers/telemetry_census.py`

Source: `agora.intelligence_outputs` on the canonical store
(database `prometheus_fire`, server `192.168.1.202`). Read-only SELECTs.

## stage_census_atalanta

per-stage row counts and the real per-row timeline for this agent

```
SQL: select stage, count(*) as n, count(distinct cycle_id) as cycles, min(finished_at) as first_row, max(finished_at) as last_row from agora.intelligence_outputs where stage ilike 'atalanta%' group by 1 order by 2 desc

stage | n | cycles | first_row | last_row
atalanta_upstream_not_found | 354 | 3 | 2026-05-23 04:28:00.652629-04:00 | 2026-05-30 12:10:49.022646-04:00
atalanta_self_audit_null | 305 | 1 | 2026-05-24 04:09:50.637820-04:00 | 2026-05-30 12:10:49.043886-04:00
atalanta_startup | 3 | 3 | 2026-05-23 04:28:00.615888-04:00 | 2026-05-23 04:39:46.803722-04:00
atalanta_shutdown | 1 | 1 | 2026-05-23 04:28:00.702628-04:00 | 2026-05-23 04:28:00.702628-04:00
```

## alarm_census_fleet

every anti-silence alarm row ever written, by agent

```
SQL: select stage, count(*) as n, sum(case when success = false then 1 else 0 end) as fail_rows, min(finished_at) as first_row, max(finished_at) as last_row from agora.intelligence_outputs where stage ilike '%self_audit_null%' group by 1 order by 2 desc

stage | n | fail_rows | first_row | last_row
pheme_self_audit_null | 305 | 305 | 2026-05-24 04:09:50.734328-04:00 | 2026-05-30 12:10:48.585181-04:00
atalanta_self_audit_null | 305 | 305 | 2026-05-24 04:09:50.637820-04:00 | 2026-05-30 12:10:49.043886-04:00
polyhymnia_self_audit_null | 23 | 23 | 2026-05-29 05:25:01.087168-04:00 | 2026-05-29 16:29:10.863331-04:00
talos_self_audit_null | 8 | 8 | 2026-05-29 08:54:23.839344-04:00 | 2026-05-29 15:54:29.087192-04:00
```

## dead_upstream_census_fleet

every dead-upstream / drought row ever written, by agent

```
SQL: select stage, count(*) as n, min(finished_at) as first_row, max(finished_at) as last_row from agora.intelligence_outputs where stage ilike '%upstream_not_found%' or stage ilike '%drought%' group by 1 order by 2 desc

stage | n | first_row | last_row
atalanta_upstream_not_found | 354 | 2026-05-23 04:28:00.652629-04:00 | 2026-05-30 12:10:49.022646-04:00
pheme_upstream_not_found | 354 | 2026-05-23 04:28:01.217611-04:00 | 2026-05-30 12:10:48.564293-04:00
talos_upstream_not_found | 2 | 2026-05-23 11:48:00.902479-04:00 | 2026-05-23 11:48:57.429014-04:00
```

## alarm_error_field

the error string carried by this agent's alarm rows

```
SQL: select error, success, count(*) from agora.intelligence_outputs where stage = 'atalanta_self_audit_null' group by 1, 2

error | success | count
anti_silence_threshold_exceeded | False | 305
```

## table_size

Rows in agora.intelligence_outputs at read time: 15495
