# Thesauros — The Prometheus Data Treasury

Named for θησαυρός (thesauros) — treasury, storehouse.

This directory is the master catalog of all data assets in Project Prometheus: where they live, where they came from, what state they're in, and how to access them.

## Data Architecture

```
                        ┌─────────────────┐
                        │   Consumers     │
                        │ Harmonia Ergon  │
                        │ Charon  Kairos  │
                        │ Aporia  Charon  │
                        └───────┬─────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                  │
    ┌─────────▼──────┐  ┌──────▼───────┐  ┌──────▼───────┐
    │  PostgreSQL     │  │   Redis      │  │   DuckDB     │
    │  (M1: .176)     │  │  (M1: .176)  │  │  (M2 local)  │
    │                 │  │              │  │              │
    │ lmfdb      (RO) │  │ agora:*      │  │ charon.duckdb│
    │ prometheus_sci  │  │ cache:*      │  │ (legacy)     │
    │ prometheus_fire │  │ agent:*      │  │              │
    └─────────────────┘  └──────────────┘  └──────────────┘
```

## Quick Reference

| Database | Host | Port | User | Rows | Purpose |
|----------|------|------|------|------|---------|
| lmfdb | 192.168.1.176 | 5432 | lmfdb/lmfdb | 30M+ | LMFDB mirror (read-only) |
| prometheus_sci | 192.168.1.176 | 5432 | postgres/prometheus | 855K | Normalized scientific data |
| prometheus_fire | 192.168.1.176 | 5432 | postgres/prometheus | 152K | Operational data |
| Redis | 192.168.1.176 | 6379 | password=prometheus | — | Cache, streams, agent state |
| DuckDB | local | — | — | 1.1M | Legacy (charon/data/charon.duckdb) |

## Documents

### Core Reference
| File | Contents |
|------|----------|
| [data_dictionary.md](data_dictionary.md) | **Every column in every table.** Types, meanings, caveats. Start here. |
| [provenance.md](provenance.md) | Origin tracking for all data sources |

### Database Docs
| File | Contents |
|------|----------|
| [postgres_lmfdb.md](postgres_lmfdb.md) | LMFDB mirror: 5 tables, 30M+ rows, indexes |
| [postgres_sci.md](postgres_sci.md) | prometheus_sci: scientific data, 14 tables |
| [postgres_fire.md](postgres_fire.md) | prometheus_fire: operational data, 15 tables |
| [redis.md](redis.md) | Redis namespaces, streams, cache strategy |
| [duckdb_legacy.md](duckdb_legacy.md) | DuckDB tables, migration status |

### Planning
| File | Contents |
|------|----------|
| [unified_data_plan.md](unified_data_plan.md) | **START HERE for planning.** Consolidated from all agents. 8 priorities, schemas, blockers. |
| [proposals.md](proposals.md) | Individual proposals with status tracking |
| [MIGRATION_PLAN.md](MIGRATION_PLAN.md) | DuckDB → Postgres+Redis migration detail (Agora) |
| [harmonia_data_storage_recommendation.md](harmonia_data_storage_recommendation.md) | Harmonia's three-tier storage recommendation |
| [database_architecture.md](database_architecture.md) | Original architecture design (Agora/Claude_M1) |
| [loose_files.md](loose_files.md) | Cartography data files not yet in any database |
| [data_audit_20260415.md](data_audit_20260415.md) | Raw inventory from first Mnemosyne session |
| [dataset_scan_20260418.md](dataset_scan_20260418.md) | External dataset scan — gaps and candidate ingestions ranked by leverage |
| [missing_data.md](missing_data.md) | **Missing-data registry** — datasets verified absent on M2, check M1 first |
