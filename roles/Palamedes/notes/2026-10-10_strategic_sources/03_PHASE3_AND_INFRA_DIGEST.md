# Source digest 3 -- Phase 3 designs/reviews (ASTRA-6.0, FABLE-5.1, v0.4 synthesis, wind-tunnel) + execution inventory

Prepared for Palamedes (Strategic Expansion Directive 2026-10-10) by a read-only research subagent at 361de0b20;
ASTRA design files under docs/phase3/design/ASTRA-6.0/. Citations re-read before use in a deliverable.

## Part 1 -- designs and reviews
- ASTRA-6.0: "a design and evidence synthesis, not a deployed or experimentally qualified RSE" (README:3); offline
  tests only; science NOT_VERIFIED. Post-audit recommendation: "sequential A0-first observatory with an independent
  scientific checker, not three runtimes by day 30" (RSE_ARCHITECTURE:205); D1 A first, D2 one resource regime, D3
  stronger ordinary competitors, D4 local immutable bundles + one fail-closed verifier ("do not restore Fabric, a wiki
  service, or a fleet scheduler merely for continuity", ENGINE_PORTFOLIO:36), D5 every CPU receipt assigned to a lane and
  phase. Caps (planning): 480 core-h, 0 GPU, 0 paid GPU, 30 kWh, 320 engineering-h, 21 review-h; <=4 workers, <=16 GiB,
  <=6 core-h per job; "do not start paid runs before the operator specifies one" (RSE_ARCHITECTURE:183). Binding
  constraint engineering time, not CPU (MVP_90_DAYS:344-361); throughput UNKNOWN.
- Falsifiers: adequacy certificate for a qualified negative (capacity, world demand, search, ruler, intervention,
  custody, uncertainty, resources); ruler gates sensitivity LB95 >= 0.80, false-positive UB95 <= 0.05; F01-F16; thesis
  exits at months 4-12. Open questions top 5: A0 witness, independent checking/custody staffing, qualification within
  CPU/energy/attention, curated qualification vs endogenous mechanisms, neutral-bridge crossing.
- Fable closure review v0.4: ACCEPT_WITH_MINOR_AMENDMENTS; C1-C5 (three-field receipt, relative claims, registered
  reset model, authority stages, anchor keeper); "build it, let me try to break it once, repair once, then put a real
  architecture through it".
- Wind tunnel: ASTRA charter review "Conditional GO for RSO as a thin federation ... NO-GO for a universal organism
  runtime, universal decisive scorer, or ten-engine program"; four inference-fatal flaws (write-ancestry recursion,
  scaffold recovery is not discovery, co-adapting public scorer, boundary-incomplete reset); what not to build includes
  "expensive GPU training campaign", "fleet expansion", "all-event lineage database". Fable response: "RIGHT DISCIPLINE,
  NOT YET A NEUTRAL INSTRUMENT"; "what this tunnel can certify today is memory" (:533); receipt log suffices.

## Part 2 -- execution inventory
| component | status |
|---|---|
| Fabric queue (fabric/, Postgres on M1, SKIP LOCKED, reaper; claude -p and script executors) | pilot P1-P9 PASS 2026-09-28; frozen (no scheduler); ubu001 workers "online" but dead since 2026-10-02 (ops/fleet/M1_DRAIN_2026-10-03/P2B_INTAKE.md:113) -- effectively DEAD |
| Fabric leases | exists and used (e.g. skullport:gpu0) |
| promexec broker | exists, NOT installed/enabled |
| ubu001-006 + PrometheusWorker (workgraph push-claim) | 2-4 cores, 8-22 GB, NO GPU; one smoke-test receipt only (C-005-T001); some nodes host interactive seats |
| checkpoint/restart | per-system only (Fabric requeues whole attempt; RunPod resume re-attaches to a live pod); general facility designed only |
| artifact store | Fabric blobs (16 MB cap), RunPod receipt dirs, git; no large store (git-CAS evaluation C-008 BLOCKED) |
| RunPod launcher (Aether/runpod/prometheus_gpu/, aeth01_canary/) | exists and used: >60 receipts 2026-09-22..10-05, billed ~1.004x estimate; inventory check refuses if any pod exists; terminate in finally; budget check client-side estimate (launch.py:1149-1150); account spendLimit 80; one pod at a time |
| GPUs | RTX 5060 Ti 16 GB on M1 and M2; GTX 1070 on M3; none on ubu nodes |
| rso ledger | exists and used (launches, CPU-s, bytes; no dollar field; single writer) |
| ops/fleet tooling | staleness reports, worktree inventory; not cost accounting |
| dollar ledger | MISSING fleet-wide |
| custody registry (ops/custody, hash-chained, Aporia registrar) | exists and used; shared superuser: tampering detected not prevented |
| cloud CPU (Azure) | designed only; waiting on operator spend ceiling |

Spending rules: directive 2026-10-10 :291, :299, :305, :307, :658; MWO-0004 R2 standing envelope (local/unpaid only,
Fabric lease, <= 16 CPU core-h per item) and G4 "No RunPod or other paid compute"; per-directive caps (Techne $10,
Aether canary <= $3); infra/FLEET_HOSTS.md:64-71 internal fleet first.
