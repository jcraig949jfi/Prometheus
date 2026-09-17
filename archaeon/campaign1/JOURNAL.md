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

## 01:50-02:45 -- SFE-02 (two attempts; INCONCLUSIVE)

- Attempt 1 (stream 1024, 21 s) and attempt 2 (stream 4096, 35 s, D-009):
  engine path 0 errors both times (16 artifacts, 12 experiments + 12
  observations per attempt, world TERMINATED in 0.2 s; identical sealed
  manifest deduplicated by content hash across attempts).
- Science: solve fraction 0 for every policy; whole-stream ceiling < 0.5
  on every query (max 0.21) -> assay incapable -> INCONCLUSIVE by the
  prereg rule. Diversity landscape real: behavioral 32 cells, hybrid
  25-28, uniform 17-20, top_k 10-17 under one cap; count cap bound every
  policy, byte cap never. Record: SFE-02/RECORD.md. Ledger L-014..L-016,
  L-012 recurrence 1. Next: SFE-03.

## 02:45-03:20 -- SFE-03 (one attempt; INCONCLUSIVE)

- 127.6 s; engine 0 errors (3 worlds, 6 failure artifacts under
  FAILURES_ONLY, 6 imports, 9 experiments + 9 observations, teardown
  0.49 s). All nine rows at the chance floor (W1_d4 unreachable by fresh
  search at N=200 G=60, as v01 and SSF c3 already showed) -> assay
  incapable -> INCONCLUSIVE. Memorisation shelf visible in train-vs-held
  split (transported episodes recur every generation). Ledger L-017;
  L-009 recurrence 1 (my digest check again). Next: SFE-04.

## 03:20-03:40 -- SFE-04 (one attempt; COMPLETE)

- 5.5 s; engine 0 errors (1 world, 2 artifacts, 3 experiments + 3
  observations, teardown 0.22 s). q1 useful computation weak positive
  (particle2 0.608 vs 0.500 controls; shift 1.000); q2 NO localized
  component: every 5-cell window costs ~0.10 = the matched random-lesion
  band (max 0.113), shift-register control localizes at 0.500; q3 frozen
  whole-substrate reuse positive on delay 3 (0.583 vs 0.483), localized
  reuse null. D-010 (D-18 v1 reset; linear task). Ledger L-018..L-020.
  Next: SFE-05.

## 03:40-04:25 -- SFE-05 (one engine attempt; COMPLETE)

- Two dry runs first: the first showed the transfer set saturating every
  delay (D-012: knob -> distractor count). Engine run 86 s, 0 errors, 13
  artifacts, 12 experiments + 12 observations, world TERMINATED.
- adaptive main +0.155, transfer main +0.113, interaction +0.042 (n=3);
  forgetting shelf: fixed/on loses Kd-0 competence (0.00-0.04) while
  adaptive/on keeps it (0.38-1.00) and climbs to Kd 4 in 2/3 seeds.
  Ledger L-021 (generation-step API), L-022 (rung x generation matrix);
  L-008 recurrence with mitigation. Next: SFE-06.

## 04:25-04:45 -- SFE-06 (one engine attempt; COMPLETE)

- 4.9 s; engine 0 errors (1 world, 6 artifacts incl. sha256-identified
  decoder tables, 9 experiments + 9 observations). Fixed evaluator (block
  output, rule 184 = 1.000 reachable): direct hits >= 0.9 in 13/53/53
  evaluations, balanced 653/97/89 with 50% more accessible variation,
  scrambled 971/-/190 (2/3). Encoding effect weak positive; accessible
  variation decoupled from navigability. Ledger L-023, L-024. Next: SFE-07.

## 04:45-05:05 -- SFE-07 (two attempts; COMPLETE)

- Attempt 1 (9.3 s): SFE-01's failure artifacts unreadable from the new
  session (403 SESSION_MISMATCH; L-026); probe showed a session-less read
  is admitted (D-013). Attempt 2 (13.4 s): 135 failed genotypes fetched
  from the TERMINATED SFE-01 world, hashes 3/3 OK; 0 errors.
- Science: failed_A seeds World B (W3_K2) in 2/3 seeds (0.58/0.56) vs
  random 0/3; specialized_A and best_A transfer by direct reuse
  (0.52-0.58). Predeclaration artifact precedes everything. Ledger
  L-025, L-026; L-012/L-013 recurrences. Next: SFE-08.

## 05:05-05:25 -- SFE-08 (one engine attempt; COMPLETE)

- 23.8 s; engine 0 errors (1 world, 3 composed-set artifacts with
  per-member provenance, 18 experiments + 18 observations). Chimera
  synergy NEGATIVE: chimera_XY = shuffled_organs = random_recomb at the
  floor (0/3 each) while ancestors L2/L3 seed footholds (1/3 each, gens
  39/11): the whole failed genotype is the search material, not its
  2-4-instruction organs. Ledger L-027. Next: SFE-09.

## 05:25-05:55 -- SFE-09 (one engine attempt; INCONCLUSIVE)

- 73 s; engine 0 errors (1 world, representation descriptor artifact, 18
  experiments + 18 observations). No representation reached the reachable
  control cell (0/3 x 3); the baseline solved the 'stuck' cell once
  (seed 1, gen 52); B/C 0/6. Positive control failed -> INCONCLUSIVE;
  'stuck' is 1/12 pooled. Ledger L-028, L-029; L-017 recurrence 1.
  Next: SFE-10.

## 05:55-06:25 -- SFE-10 (two engine attempts; COMPLETE, NEGATIVE)

- attempt 1 66 s, attempt 2 52 s; engine 0 errors both (3 worlds, 12
  artifacts, 12 hash-verified imports, 15 experiments + 15 observations).
  Attempt 1's harness filled the pc arms' generation 0 from its own seed
  (L-030, CRN broken; D-014 rerun). Attempt 2: mono 3/3 footholds (gens
  48-54) vs pc_0.4 1/3, pc_0.2 0/3. The one mature artifact (W0 solved
  at 1.0) bought a foothold at charged gen 30 vs 50; immature artifacts a
  loss. Ledger L-030..L-032; L-008 recurrence 2, L-012 recurrence 3.
  Next: campaign report.
