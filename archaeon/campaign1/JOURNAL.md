# Campaign 1 -- journal (SFE autonomous ten-experiment campaign)

Directive: roles/Archaeon/prompts/2026-09-17_sfe_campaign1/00_OPERATOR_DIRECTIVE.md
Decisions: archaeon/campaign1/DECISIONS.md. Ledger: archaeon/campaign1/LEDGER.jsonl
(one JSON object per finding; schema in LEDGER_SCHEMA.md). Per-experiment
records: archaeon/campaign1/SFE-NN/ (RECORD.md in the directive's A-F shape,
plus rows/receipts). Every timestamp UTC.

## 00:05-00:15 -- campaign open

- Seat Archaeon[m2-411504ab], worktree D:/Prometheus-worktrees/archaeon-wse-2026-09-16,
  branch archaeon/wse-2026-09-16, base of the day cb91659ef, HEAD at open 37ca43bd4.
- Environment survey (00:10 UTC): engine LIVE at https://192.168.1.191:8811
  (eng_906356f7, build 4dbcd3fd, schema 8, registration_open, uptime 6.8 h,
  826 requests, 0 5xx, 118 4xx, last ledger event 6.8 h ago, ledger
  D:\Prometheus-data\sfe\engine.db). Comms: 0 new; every other seat offline
  (last syncs 2026-09-14..16). Vivarium consumer on M2: PREPARED, NOT
  LAUNCHED (MONITORS row). PEW on M2 :8377 (Mnemosyne #290).
- D-001..D-004 recorded (charter suspension for campaign machinery; live
  engine + own client; 4 h / 24 h timebox; standalone fallback labelled).
- Substrate survey delegated (SFE client API, conformance gate, H0-H5
  harnesses, Vivarium executors callable directly, PEW write path).
