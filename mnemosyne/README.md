# Mnemosyne — Working Directory
## DBA & Data Steward workspace

This directory contains Mnemosyne's working files: data audits, ingestion scripts,
migration plans, and operational logs.

## Current Status (2026-04-15)

### Connected
- LMFDB Postgres (M1): 3,824,372 EC rows confirmed
- DuckDB (local): 14 tables, 134K objects
- Redis (M1): Connected, Agora streams operational

### Blocked
- prometheus_sci: Database not yet created (needs `sudo -u postgres psql -f scripts/db_setup.sql` on M1)
- prometheus_fire: Same blocker

### Data Inventory
See `data_audit_20260415.md` for complete inventory of files available for ingestion.
