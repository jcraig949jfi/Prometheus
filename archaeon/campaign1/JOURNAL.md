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

## 00:15-01:50 -- SFE-01 (two attempts; COMPLETE)

- Gate: Harmonia's conformance_check.py vs live M2 with 20 declared
  routes: CONFORMANT (68/68, 30 GET scoping probes match).
- Attempt 1 (100 s): engine path clean except 3x 422 on POST failures
  (L-006); science void: cell label seeded the RNG (L-008), exact-genome
  tabu inert (L-007), my hash check wrong (L-009). Preserved as
  RECEIPT_attempt1.json / rows_attempt1.json.
- Attempt 2 (170 s, D-007/D-008): 0 errors, 12/12 imports hash-verified,
  7/7 worlds TERMINATED. Components WEAK POSITIVE (2/3 footholds vs 0/3
  random-segment control, 1/3 baseline), failures NULL/NEGATIVE,
  interaction not estimable (n=3). Full record: SFE-01/RECORD.md.
- Ledger L-001..L-013. Next: SFE-02.
