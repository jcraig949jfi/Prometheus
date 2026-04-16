# prometheus_fire — Operational Data

**Database:** prometheus_fire  
**Host:** 192.168.1.176:5432  
**User:** postgres / prometheus  
**Access:** Read-write  
**Total rows:** ~152K  

This is the only read-write database. Back it up.

## Schema: xref (Cross-references)

| Table | Rows | Key Columns |
|-------|------|-------------|
| object_registry | 134,475 | object_id, source_db, source_table, source_key, object_type |
| bridges | 17,314 | bridge_id, source_object_id, target_object_id, bridge_type, evidence_grade, confidence, provenance |

Source: Migrated from DuckDB `objects` and `known_bridges` tables via `mnemosyne/migrate_m2.py`.

## Schema: agora (Communication)

| Table | Rows | Key Columns |
|-------|------|-------------|
| messages | 60 | stream_id, sender, msg_type, subject, body, confidence, created_at |
| decisions | 3 | title, status, proposer, reviewer, summary, evidence |
| open_questions | 1 | title, proposer, challenger, decisive_test, status |
| agent_sessions | 0 | agent_name, machine, connected_at, working_on |

## Schema: results (Science output)

| Table | Rows | Key Columns |
|-------|------|-------------|
| ergon_runs | 0 | run_id, n_generations, n_tested, n_cells, max_depth, config (JSONB) |
| hypotheses | 0 | domain_a/b, feature_a/b, coupling, z_score, p_value, survival_depth, kill_test, fitness |
| harmonia_bonds | 0 | domain_a/b, bond_dim, surviving_rank, top_singular_values[], scorer_type, falsification_tests (JSONB) |

## Schema: kill (Failure tracking)

| Table | Rows | Key Columns |
|-------|------|-------------|
| taxonomy | 0 | hypothesis_type, failure_mode, f_test, domain, constraint_added |
| shadow_cells | 0 | cell_key, domain_a/b, feature_a/b, n_tested, n_survived, best_depth, dominant_kill, confidence |

## Schema: tensor (Feature metadata)

| Table | Rows | Key Columns |
|-------|------|-------------|
| domain_features | 0 | object_id, domain, feature_name, value |
| domain_metadata | 0 | domain, n_objects, n_features, feature_names[], build_timestamp |

## Schema: meta (Operations)

| Table | Rows | Key Columns |
|-------|------|-------------|
| calibration | 0 | theorem_name, expected_result, observed_result, passed |
| ingestion_log | 4 | source_name, table_name, rows_loaded, duration_s, status, error |

## Backup

```bash
# Run on M1:
pg_dump -U postgres prometheus_fire > ~/backups/prometheus_fire_$(date +%Y%m%d).sql
```
